// The news signup, written once: every page that offers it has <div class="signup">, and
// this fills it in. The list is kept by Buttondown; to move to another service, change
// ACTION (and the field names, if the new one wants others). Without JavaScript the box
// stays empty and the page still says how to reach us.
(function(){
  var ACTION='https://buttondown.com/api/emails/embed-subscribe/muthuraman';
  document.querySelectorAll('.signup').forEach(function(box,i){
    var place=box.dataset.place||'page', id='signup-'+i;
    box.innerHTML=
      '<form class="notify" method="post" target="_blank" action="'+ACTION+'">'
      +'<label for="'+id+'" class="label" style="flex-basis:100%">Tell me when designed experiments arrive</label>'
      +'<input id="'+id+'" type="email" name="email" placeholder="you@university.edu" autocomplete="email" required>'
      +'<input type="text" name="metadata__study" placeholder="What do you study? (optional)" aria-label="What do you study? (optional)">'
      +'<input type="hidden" name="tag" value="'+place+'">'
      +'<button type="submit">Notify me</button>'
      +'</form>'
      +'<p class="notify-note">One email when experiments are released: run each version many times and get one table. '
      +'Unsubscribe any time. Or <a href="https://github.com/teamrunner/teamrunner">watch the repository on GitHub</a>.</p>';
    box.querySelector('form').addEventListener('submit',function(){
      if(window.goatcounter&&window.goatcounter.count)
        window.goatcounter.count({path:'signup-'+place,title:'signup-'+place,event:true});
    });
  });
})();
