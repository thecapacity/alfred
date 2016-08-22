javascript:(function(){
    tags = prompt('Tags','')
    // location.href=
    //href='https://localhost:5000/entries?url='
    href='{{ url_for('entries', _external=True) }}'+'?url='
                    +encodeURIComponent(location.href)
                    +'&title='+encodeURIComponent(document.title)
                    +'&tags='+encodeURIComponent(tags);
    alert(href);
})();
