
// VARIABLE VERTICAL ALIGNMENT
(function ($) {
	$.fn.valign = function() {
		return this.each(function(i){
		var ah = $(this).height();
		var ph = $(this).parent().height();
		var mh = (ph - ah) / 2;
		$(this).css('margin-top', mh);
		});
	};
})(jQuery);


//
//
// FUNCTIONS FOR REPLY/ATTACH
//
//

// CLOSE REPLY FUNCTION
function closeReplyform (replytype,parentid) {
	var dropdown = "#"+parentid+" div."+replytype+"div";
	
	$(dropdown).animate({
		height: 0,
		overflow: 'hidden'
	}, 150, function() {
		$(dropdown).html("").removeClass("opened");
	});
}

			
// OPEN REPLY FUNCTION
function openReplyform (replytype,parentid) {				
				
	var contents = $("div#"+replytype+"form").html();
	var dropdown = "#"+parentid+" div."+replytype+"div";
	
	$(dropdown).animate({
		height: "100px",
		overflow: 'hidden'
	}, 150, function() {
		$(dropdown).html(contents).addClass("opened");
		$(dropdown).append('<a href="javascript:closeReplyform(\''+replytype+'\',\''+parentid+'\');" class="closereply">close</a>');
		var pkid = parentid.substr(8);
		$(dropdown+" form #id_in_reply_to").attr("value",pkid);
	});
}

// ATTACH FUNCTIONS TO LINKS
function handleReplyform() {
	var parentid = $(this).closest("li.comment").attr("id");
	
	if ($(this).hasClass("attach")) { var replytype = "attach"; }
		else { var replytype = "reply"; }
						
	
	if ($("#"+parentid+" ."+replytype+"div").hasClass("opened")) {
		closeReplyform(replytype,parentid);
		return false;
	}

	openReplyform(replytype, parentid);	
	return false;
}