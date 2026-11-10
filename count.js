// What teamrunner.ai counts, besides page views (GoatCounter: no cookies,
// nothing that identifies a visitor; localhost and file:// are never counted).
// Named clicks show up in GoatCounter as events:
//   copy-<os>-<step>   a Copy button on install.html (data-count on the button)
//   out-pypi, out-github, out-issues   links that leave the site
//   tutorial-browser, tutorial-terminal   the tutorial's "follow in" switch
//   tutorial-copy-<step>   text copied from a command or file on a tutorial step page
//   signup-<place>   the news signup sent (signup.js)
(function(){
  function count(name){
    if(window.goatcounter&&window.goatcounter.count)
      window.goatcounter.count({path:name,title:name,event:true});
  }
  document.addEventListener('click',function(e){
    var t=e.target; if(!t.closest) return;
    var b=t.closest('button[data-count]');
    if(b){count(b.dataset.count);return}
    var v=t.closest('.via-switch button[data-via]');
    if(v){count('tutorial-'+v.dataset.via);return}
    var a=t.closest('a[href]');
    if(a){
      if(a.hostname==='pypi.org') count('out-pypi');
      else if(a.hostname==='github.com') count(a.pathname.indexOf('/issues')>=0?'out-issues':'out-github');
    }
  },true);
  document.addEventListener('copy',function(e){
    var m=document.querySelector('main[data-step]'), t=e.target;
    if(!m||m.dataset.step==='0'||!t||!t.closest) return;
    if(t.closest('code.cmd, pre, .diff')) count('tutorial-copy-'+m.dataset.step);
  });
})();
