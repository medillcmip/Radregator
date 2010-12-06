function loadScripts(array,callback){
    var loader = function(src,handler){
        var script = document.createElement("script");
        script.src = src;
        script.onload = script.onreadystatechange = function(){
        script.onreadystatechange = script.onload = null;
                handler();
        }
        var head = document.getElementsByTagName("head")[0];
        (head || document.body).appendChild( script );
    };
    (function(){
        if(array.length!=0){
                loader(array.shift(),arguments.callee);
        }else{
                callback && callback();
        }
    })();
}



(function(){

    loadScripts([
        'http://localhost:8000/static/js/jquery.js',
         //'http://localhost:8000/static/js/jquery-ui-1.8.6.custom.min.js'
        'http://ajax.googleapis.com/ajax/libs/jqueryui/1.7.1/jquery-ui.min.js'
    ],function(){
        $('head').append('<link rel="stylesheet" type="text/css" href="http://ajax.googleapis.com/ajax/libs/jqueryui/1.7.1/themes/base/jquery-ui.css">');
        //$("#srcr_contrib_1").append("<div id='dialog_1'>TEST TEST TEST</div>");
        //$("#dialog_1").dialog();
        var $dialog = $('<div></div>')
            .html('<iframe src="http://localhost:8000/contribution_summary/1/" width="100%" height="100%" frameborder="0"></iframe>')
            .dialog({
                autoOpen: true,
                title: 'Srcrer'
        });

    });


})();
