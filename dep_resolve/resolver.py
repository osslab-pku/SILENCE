import logging

from typing import List, Set, Dict, Optional, Union, Any
from datetime import datetime
from datetime import timezone
from pymongo import MongoClient
from packaging.requirements import Requirement, InvalidRequirement
from packaging.version import parse as parse_version, InvalidVersion


logger = logging.getLogger(__name__)


class Dependency:
    def __init__(self, name: str, version: str, constraints: Set[str]):
        self.name = name
        self.version = version
        self.constraints = constraints


class DependencyResolver:
    def __init__(self, mongo_uri):
        self.mongo_uri = mongo_uri
        self.mongo_client = MongoClient(mongo_uri, tz_aware=True)

    def match_version(
        self, req: Requirement, before: datetime
    ) -> Union[Optional[str], List[str]]:
        package_db = self.mongo_client["license"]["package"]
        candidates = []
        for metadata in package_db.find({"name": req.name.lower()}):
            if metadata["release_date"] > before:
                continue
            try:
                if req.specifier is None or metadata["version"] in req.specifier:
                    candidates.append((metadata["version"], metadata["requires_dist"]))
            except InvalidVersion:
                continue
        if len(candidates) == 0:
            return None, None
        else:  # latest version
            return sorted(candidates, key=lambda x: parse_version(x[0]))[-1]

    def resolve(
        self,
        require_dist: List[str],
        extras: Set[str] = None,
        before: datetime = datetime.now(tz=timezone.utc),
    ) -> Dict[str, Dict[str, Any]]:
        extras = set() if extras is None else extras
        resolved = {}
        req_queue = [("", d) for d in reversed(require_dist)]

        while len(req_queue) > 0:
            try:
                src_pkg, req = req_queue.pop(0)
                req = Requirement(req)
            except InvalidRequirement:
                logger.warn("Invalid requirement: %s", req)
                continue
            constraint = {
                "from": src_pkg,
                "specifier": str(req.specifier),
            }

            if req.marker is not None and not req.marker.evaluate():
                continue
            if req.extras is not None and not req.extras.issubset(extras):
                continue

            # TODO: ignores dependency conflicts, may need to address later
            if req.name in resolved:
                resolved[req.name]["constraints"].append(constraint)
                continue

            version, next_require = self.match_version(req, before)
            if version is None:
                logger.warn("No matched version for %s before %s", req, before)
                continue
            resolved[req.name] = {"version": version, "constraints": [constraint]}
            req_queue.extend([(req.name, next) for next in reversed(next_require)])
            logger.debug("Resolved %s-%s", req.name, version)

        return resolved

    def __del__(self):
        self.mongo_client.close()
