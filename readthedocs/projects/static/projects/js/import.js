require=function o(s,i,u){function l(r,e){if(!i[r]){if(!s[r]){var t="function"==typeof require&&require;if(!e&&t)return t(r,!0);if(c)return c(r,!0);var n=new Error("Cannot find module '"+r+"'");throw n.code="MODULE_NOT_FOUND",n}var a=i[r]={exports:{}};s[r][0].call(a.exports,function(e){return l(s[r][1][e]||e)},a,a.exports,o,s,i,u)}return i[r].exports}for(var c="function"==typeof require&&require,e=0;e<u.length;e++)l(u[e]);return l}({1:[function(e,r,t){var o=e("jquery");function a(e){var n=o.Deferred(),a=5;return setTimeout(function t(){o.getJSON(e.url).done(function(e){e.finished?e.success?n.resolve():n.reject({message:e.error}):setTimeout(t,2e3)}).fail(function(e){if(console.error("Error polling task:",e),0<(a-=1))setTimeout(t,2e3);else{var r=e.responseJSON.detail||e.statusText;n.reject({message:r})}})},2e3),n}r.exports={poll_task:a,trigger_task:function(e){var t=o.Deferred(),r=e.url,n={csrfmiddlewaretoken:e.token};return $.ajax({method:"POST",url:r,data:n,success:function(e){a(e).then(function(){t.resolve()}).fail(function(e){t.reject(e)})},error:function(e){var r=e.responseJSON.detail||e.statusText;t.reject({message:r})}}),t}}},{jquery:"jquery"}],"projects/import":[function(e,r,t){var i=e("knockout"),u=e("jquery"),n=e("readthedocs/core/static-src/core/js/tasks");function l(e,r){var t=u("<a>").attr("href",e).get(0);return Object.keys(r).map(function(e){t.search&&(t.search+="&"),t.search+=e+"="+r[e]}),t.href}function c(e,r){var t=this;t.id=i.observable(e.id),t.name=i.observable(e.name),t.slug=i.observable(e.slug),t.active=i.observable(e.active),t.avatar_url=i.observable(l(e.avatar_url,{size:32})),t.display_name=i.computed(function(){return t.name()||t.slug()}),t.filter_id=i.computed(function(){return t.id()}),t.filter_type="org",t.filtered=i.computed(function(){var e=r.filter_by();return e.id&&e.id!==t.filter_id()||e.type&&e.type!==t.filter_type})}function p(e,r){var t=this;t.id=i.observable(e.id),t.username=i.observable(e.username),t.active=i.observable(e.active),t.avatar_url=i.observable(l(e.avatar_url,{size:32})),t.provider=i.observable(e.provider),t.display_name=i.computed(function(){return t.username()}),t.filter_id=i.computed(function(){return t.provider().id}),t.filter_type="own",t.filtered=i.computed(function(){var e=r.filter_by();return e.id&&e.id!==t.filter_id()||e.type&&e.type!==t.filter_type})}function a(e,a){var o=this;o.id=i.observable(e.id),o.name=i.observable(e.name),o.full_name=i.observable(e.full_name),o.description=i.observable(e.description),o.vcs=i.observable(e.vcs),o.default_branch=i.observable(e.default_branch),o.organization=i.observable(e.organization),o.html_url=i.observable(e.html_url),o.clone_url=i.observable(e.clone_url),o.ssh_url=i.observable(e.ssh_url),o.matches=i.observable(e.matches),o.match=i.computed(function(){var e=o.matches();if(e&&0<e.length)return e[0]}),o.private=i.observable(e.private),o.active=i.observable(e.active),o.admin=i.observable(e.admin),o.is_locked=i.computed(function(){return a.has_sso_enabled?!o.admin():o.private()&&!o.admin()}),o.avatar_url=i.observable(l(e.avatar_url,{size:32})),o.import_repo=function(){var t={name:o.name(),repo:o.clone_url(),repo_type:o.vcs(),default_branch:o.default_branch(),description:o.description(),project_url:o.html_url(),remote_repository:o.id()},n=u("<form />");n.attr("action",a.urls.projects_import).attr("method","POST").hide(),Object.keys(t).map(function(e){var r=u("<input>").attr("type","hidden").attr("name",e).attr("value",t[e]);n.append(r)});var e=u("<input>").attr("type","hidden").attr("name","csrfmiddlewaretoken").attr("value",a.csrf_token);n.append(e);var r=u("<input>").attr("type","submit");n.append(r),u("body").append(n),n.submit()}}function o(e,r){var s=this;s.config=r||{},s.urls=r.urls||{},s.csrf_token=r.csrf_token||"",s.has_sso_enabled=r.has_sso_enabled||!1,s.error=i.observable(null),s.is_syncing=i.observable(!1),s.is_ready=i.observable(!1),s.page_current=i.observable(null),s.page_next=i.observable(null),s.page_previous=i.observable(null),s.filter_by=i.observable({id:null,type:null}),s.accounts_raw=i.observableArray(),s.organizations_raw=i.observableArray(),s.filters=i.computed(function(){var e,r=[],t=s.accounts_raw(),n=s.organizations_raw();for(e in t){var a=new p(t[e],s);r.push(a)}for(e in n){var o=new c(n[e],s);r.push(o)}return r}),s.projects=i.observableArray(),i.computed(function(){var e=s.filter_by(),r=s.page_current()||s.urls["remoterepository-list"];s.page_current()||("org"===e.type&&(r=l(s.urls["remoterepository-list"],{org:e.id})),"own"===e.type&&(r=l(s.urls["remoterepository-list"],{own:e.id}))),s.error(null),u.getJSON(r).done(function(e){var r,t=[];for(r in s.page_next(e.next),s.page_previous(e.previous),e.results){var n=new a(e.results[r],s);t.push(n)}s.projects(t)}).fail(function(e){var r=e.responseJSON.detail||e.statusText;s.error({message:r})}).always(function(){s.is_ready(!0)})}).extend({deferred:!0}),s.get_organizations=function(){u.getJSON(s.urls["remoteorganization-list"]).done(function(e){s.organizations_raw(e.results)}).fail(function(e){var r=e.responseJSON.detail||e.statusText;s.error({message:r})})},s.get_accounts=function(){u.getJSON(s.urls["remoteaccount-list"]).done(function(e){s.accounts_raw(e.results)}).fail(function(e){var r=e.responseJSON.detail||e.statusText;s.error({message:r})})},s.sync_projects=function(){var e=s.urls.api_sync_remote_repositories;s.error(null),s.is_syncing(!0),n.trigger_task({url:e,token:s.csrf_token}).then(function(e){s.get_organizations(),s.get_accounts(),s.filter_by.valueHasMutated()}).fail(function(e){s.error(e)}).always(function(){s.is_syncing(!1)})},s.has_projects=i.computed(function(){return 0<s.projects().length}),s.next_page=function(){s.page_current(s.page_next())},s.previous_page=function(){s.page_current(s.page_previous())},s.set_filter_by=function(e,r){var t=s.filter_by();t.id===e?(t.id=null,t.type=null):(t.id=e,t.type=r),s.filter_by(t),t.id&&s.page_current(null)}}u(function(){var t=u("#id_repo"),n=u("#id_repo_type");t.blur(function(){var e,r=t.val();switch(!0){case/^hg/.test(r):e="hg";break;case/^bzr/.test(r):case/launchpad/.test(r):e="bzr";break;case/trunk/.test(r):case/^svn/.test(r):e="svn";break;default:case/github/.test(r):case/(^git|\.git$)/.test(r):e="git"}n.val(e)})}),o.init=function(e,r,t){var n=new o(r,t);return n.get_accounts(),n.get_organizations(),i.applyBindings(n,e),n},r.exports.ProjectImportView=o},{jquery:"jquery",knockout:"knockout","readthedocs/core/static-src/core/js/tasks":1}]},{},[]);