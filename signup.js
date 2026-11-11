// The news signup, written once: every page that offers it has <div class="signup">, and
// this fills it in. The address is saved to a Google Sheet we own, by the small script in
// that Sheet (kept beside this site as signup-sheet.gs); nothing is sent to the person and
// the page does not change address. To move the list elsewhere, change SAVE (and the field
// names, if the new place wants others). Without JavaScript the box stays empty and the
// page still says how to reach us.
(function(){
  var SAVE='https://script.google.com/macros/s/AKfycbx4ASTMvxkyx5r-B0RNG78M35z806bNGuUkPdQ_EY5MaNzJ1CnhHEEAdcj9zdG-GFk/exec';  // the Sheet's web app address: https://script.google.com/macros/s/.../exec
  document.querySelectorAll('.signup').forEach(function(box,i){
    var place=box.dataset.place||'page', id='signup-'+i;
    box.innerHTML=
      '<form class="notify">'
      +'<label for="'+id+'" class="label" style="flex-basis:100%">Keep me posted</label>'
      +'<input id="'+id+'" type="email" name="email" placeholder="Email" autocomplete="email" required>'
      +'<input type="text" name="website" tabindex="-1" autocomplete="off" aria-hidden="true" style="display:none">'
      +'<button type="submit">Notify me</button>'
      +'</form>'
      +'<p class="notify-done" role="status" hidden></p>'
      +'<p class="notify-note">One email when experiments are released: run each version many times and get one table. '
      +'Unsubscribe any time. Or <a href="https://github.com/teamrunner/teamrunner">watch the repository on GitHub</a>.</p>';
    var form=box.querySelector('form'), done=box.querySelector('.notify-done'), button=form.querySelector('button');
    function say(html){ done.innerHTML=html; done.hidden=false; }
    function failed(){
      button.disabled=false;
      say('That did not go through. Please try again, or write to <a href="mailto:hello@teamrunner.ai">hello@teamrunner.ai</a>.');
    }
    form.addEventListener('submit',function(ev){
      ev.preventDefault();
      if(!SAVE){ failed(); return; }
      button.disabled=true;
      var body=new URLSearchParams({email:form.email.value.trim(),place:place,website:form.website.value});
      // The Sheet is on another site, so the page cannot read its answer; a request that
      // left without a network error is taken as saved.
      fetch(SAVE,{method:'POST',mode:'no-cors',body:body}).then(function(){
        form.hidden=true;
        say('You are on the list. We will write once, when experiments are released.');
        if(window.goatcounter&&window.goatcounter.count)
          window.goatcounter.count({path:'signup-'+place,title:'signup-'+place,event:true});
      },failed);
    });
  });
})();
