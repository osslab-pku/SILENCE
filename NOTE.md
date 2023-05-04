## Developer Discussions about the License Incompatibilities

### Summary (Both Proposed (Non-Implemented) and Implemented)

* **Change Own License:** ++
* **Migrate to Another Dependency:** ++++++++++
* **Negotiate With Upstream:** +++
* **Remove Dependency:** +++++
* **Pin Old Version:** +
* **Upgrade Version:** +
* **Deem as No Incompatibility (Dual license, optional dependency, etc.):** +++

### Procedure

Search GitHub issue tracker for relevant issues -> read and identify relevant text

### ansible-lint -> ansible

1. https://github.com/ansible/ansible-lint/issues/1188 
2. https://github.com/ansible/ansible-lint/discussions/1832

> While the parts of ansible-lint which are under GPL-compatible free software licenses such as the Expat (aka MIT) license may remain under that license, the work as a whole must be distributed under the terms of the GPL when incorporating GPL'd works.

**Final Resolution**: Change from MIT to GPLv3

### apache-airflow-providers-mysql -> mysql-connector-python

1. https://github.com/apache/airflow/issues/9898

> However, all these dependencies are extras and have to be installed with apache-airflow[mysql] for example, so that might not be an issue

**Proposed Resolutions**: Migrate to another dependency

> mysql-connector-python v8.0.18 - that's an interesting one. We have also mysqlclient (also GPL) to connect for MySQL operator. But we do not rely on either to connect to our MetaData store even if MySQL is used as the backend. This entirely depends on the configuration of SQL Alchemy connection string. There are many engines you can use for MySQL and there is for example https://github.com/PyMySQL/PyMySQL which is MIT licence.

### cvxpy -> ecos

1. https://github.com/cvxpy/cvxpy/issues/313

> I have switched cvxpy from GPLv3 to Apache 2.0. cvxpy does not import the ecos interface or any other solver interface unless the user has installed that solver and tries to use it. My judgment then is that if cvxpy is used without any GPLv3 solver installed the Apache 2.0 license is valid. I'm happy to discuss this further in another forum.

> GPL deals with the runtime image. Even if you have an interface this will mean you have to be GPL if they are in the same process. If the interface use IPC where ECOS and your code is in 2 different processors then you might be able to consider a different license. Is ECOS many times better than the alternatives for the trouble? Will IPC approach retain the benefit?

**Proposed Resolutions**: Migrate to another dependency

### dvc -> grandalf

1. https://github.com/iterative/dvc/issues/1115

> grandalf is dual-licensed GPL or EPL. EPL is permissive I believe. Please, check this link: https://github.com/bdcht/grandalf/blob/master/LICENSE .

### fbprophet -> lunardate, pystan

1. https://github.com/facebook/prophet/issues/1069
2. https://github.com/facebook/prophet/issues/1221
3. https://github.com/facebook/prophet/pull/1091

**Final Resolution**: Migrate to another dependency

> As of v0.6 (now on PyPI), it is possible to use fbprophet with cmdstanpy (BSD licene) instead of PyStan

> Replace instances of lunardate.LunarDate(year, month, day).toSolar() with LunarCalendar.Converter.Lunar2Solar(Lunar(year, month, day)).to_date(). Remove dependency on lunardate and add dependency on LunarCalendar>=0.0.9.
>
> Switch dependencies from lunardate (GPL) to LunarCalendar (MIT License).

### formulas -> regex

1. https://github.com/vinci1it2000/formulas/issues/33

> The Apache license is one of the upstream compatible licenses of the EUPL. Hence, the "derivative work" has to be redistributed under the EUPL.

### halo -> cursor

1. https://github.com/manrajgrover/halo/issues/118

**Proposed Resolutions**: Pin to older version, migrate to another dependency

> I'd suggest to at least freeze the cursor dependency to version 1.2.0 (the last non-GPL version). Or use something like vistir, which unfortunately is a bit heavier, but comes in quite handy in a lot of cases.

**Final Resolution**: Remove dependency

> Please remove this dependency, not only it makes your code "heavier", but also someone who incorporates your code into theirs might run into legal issues.

> I've removed halo's dependency on cursor and have directly used a StackOverflow response on which that repo was based. This resolves this issue.

### jiwer -> levenshtein

1. https://github.com/jitsi/jiwer/issues/69
2. https://github.com/jitsi/jiwer/pull/71

**Final Resolution**: Migrate to Another Dependency

> Thanks for sharing. I'm planning to move away from the dependency as soon as possible.

> move to rapidfuzz library #71

### mitmproxy -> html2text

1. https://github.com/mitmproxy/mitmproxy/issues/2572

**Final Resolution**: Remove dependency

> Can we resolve this incompatible licensing issue? html2text is barely used. I think it could be removed.

### netcdf4 -> cftime

1. https://github.com/Unidata/netcdf4-python/issues/1073
2. https://github.com/Unidata/netcdf4-python/issues/1000

**Reason for Incompatibility**: Upstream license change

> Since version 1.4, the specific code for cftime was split into a separate repository (https://github.com/Unidata/cftime), and later cftime added a small portion of GPL code to handle the leap years in version 1.0.2. The inclusion of this code implies that cftime changed its license from HPND to GPL when this code snippet was added (as cftime would be considered a derivative work of this GPL snippet).

**Proposed Resolutions**: Migrate to another dependency, negotiate with upstream, change own license

> The GPL license in cftime was inherited from calcalcs. Unless we switch to another algorithm for the calendar calculations we can't change the license.

> If this is a problem for you, you could ask the author of calcalcs to change the license.

> Update the netCDF4-python license to indicate that the package is GPL (probably not intended by the netCDF4-python developers).

> Request the cftime developers to replace the GPL snippet with equivalent code that has a license that is not propagated to derivative works.

**Final Resolution**: Negotiate with Upstream

> The next release of cftime will have the GPL'ed code replaced, and will be released under an MIT license (the same as netcdf4-python).

> cftime 1.4.0 is released under the same license as netcdf4-python, with no GPL

### orbit-ml -> pystan

1. https://github.com/uber/orbit/issues/435

**Final Resolution**: Upgrade to a newer version

> PyStan 3 benefits from an ISC license as opposed to the “viral” GPL license of PyStan 2. That alone is worth the upgrade.

### pulp -> amply

1. https://github.com/coin-or/pulp/issues/394

> However, let me rephrase this 'issue' to avoid a lengthy discussion on licensing (although I enjoy such discussions), i.e., none of us is a lawyer in the end (I am a scientist co-developing a simple python library).
>
> Since you guys also drive the development of amply, are you fine if we use the latest version of pulp and redistribute our software under GPL?

**Final Resolution**: Deem as No Incompatibility

> Just to clarify, amply itself will not be able to be sublicensed once under the EPL. @stumitchell, there is no reason for amply to be re-licensed from the COIN-OR side. The MIT license is certainly a very convenient and desirable open source license. Although most COIN-OR code is under the EPL, the MIT license is EPL-compatible. Of course, it is up to you if you want amply to be more restricted in terms of license. amply is currently not even part of COIN-OR.

### pytest-pylint -> pylint

1. https://github.com/carsongee/pytest-pylint/issues/178

**Final Resolution**: Deem as No Incompatibility

> The MIT license is a GPL compatible license, see GNU GPL compatible licenses (most people routinely call it the MIT license, GNU call it the "Expat" license, it's the same thing. See Wikipedia.

> If I understand the GNU GPL-compatible license correctly it is the other way around. You can use MIT-licensed software within a GPL-licensed project, but not the other way around, see Wikipedia

### textacy -> fuzzywuzzy, python-levenshtein, unidecode

1. https://github.com/chartbeat-labs/textacy/issues/62
2. https://github.com/chartbeat-labs/textacy/issues/63
3. https://github.com/chartbeat-labs/textacy/issues/203

**Reason for Incompatibility**: Lack of Knowledge in OSS License

**Final Resolution**: Migrate to another dependency, remove dependency

> To be totally frank, I've never really understood how the various licenses (don't) work together. I'm not using fuzzywuzzy for anything particularly fancy — just the token_sort_ratio, IIRC — so maybe it wouldn't be too much trouble to move off it. Will keep you posted.

> For what it's worth, I've decided to remove unidecode and its associated functionality from textacy: b5d3726

> Would still love a fast alternative to python-levenshtein...

### wemake-python-styleguide -> flake8-isort

1. https://github.com/wemake-services/wemake-python-styleguide/issues/2481

**Proposed Resolutions**: Negotiate with Upstream

> Have you tried to contact the flake8-isort maintainers? Maybe they will change their license ;)

**Final Resolution**: Migrate to another dependency

> I think that in this case we can just drop flake8-isort. GPL is not suitable for QA tools.

> It is easier for us to just use isort directly, which is MIT.

### workalendar -> lunardate

1. https://github.com/workalendar/workalendar/issues/346
2. https://github.com/workalendar/workalendar/issues/536
3. https://github.com/workalendar/workalendar/pull/709

**Proposed Resolutions**: Negotiate with Upstream, remove dependency

> On a longer-term level, maybe those libraries could be reimplemented from some codebase with a different license or the authors could be convinced to also use the LGPL license.

**Final Resolution**: Migrate to another dependency

> This change replaces lunardate with LunarCalendar to remove GPL-3 licensed dependency.

> This PR replaces pyCalverter, which is no more mantained and has an incompatible license (GPLv2), with convertdate.

### yt-dlp -> mutagen

1. https://github.com/yt-dlp/yt-dlp/issues/348
2. https://github.com/yt-dlp/yt-dlp/issues/2345

**Reason:** No interest

**Proposed Resolution**: Change own license, remove dependency

> Though, I do finally suggest that we remove mutagen and pycryptodome from requirements.txt or at least make them an optional dependency under another package like yt-dlp[full] or something which is listed as GPL-licensed rather than Public Domain just to be safe.

> I am just a guy trying to improve on the youtube-dl project and make my modifications available to the public. I am honestly not interested in all this copyright bullshit. But I suppose it is a part of releasing a project 😩

> Personally, I think the best licenses depending on the case are:
> 
> 1. CC0 for when you want your code released to the public domain.
> 2. MIT or Apache 2.0 if you don't mind proprietary forks of your code and prefer a permissive license. Apache 2.0 is much longer but essentially gives the same rights as MIT while including patent protection clauses and is considered legally safe by many companies due to this, when large companies collaborate in the same project.
> 3. GPLv2, GPLv2+ and GPLv3 if you want the viral aspects of the license and keeping derived works free software. I prefer GPLv3 if possible due to the patent clauses, but sometimes GPLv2+ can be a good option if you want to use code from other projects.
