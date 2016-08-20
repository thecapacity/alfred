javascript:(function(){
    tags = prompt('Tags','')
    // location.href=
    href='https://localhost:5000/entries?url='
                    +encodeURIComponent(location.href)
                    +'&title='+encodeURIComponent(document.title)
                    +'&tags='+encodeURIComponent(tags);
    alert(href);
})();
