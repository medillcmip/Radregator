
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
// LAUNCH LOG IN OVERLAY
//
//
function launchLogin () {
	$.fn.colorbox({href:'/authenticate', open:true});
}



//
//
// LOGGED IN?
//
//
//NOTE TO SELF: LOGIC NEEDS TO INCLUDE LINK PASS THROUGH/POST PASS THROUGH BEFORE IMPLEMENTATION
function authCheck() {
	$.ajax({
	    type: "post", url: "/loginstatus",
	    success: function(data){
			return;
		},
	    error: function (requestError, status, errorResponse) {
			var errorNum = requestError.status;
			
			//FINISH THIS LOGIC:
			if (errorNum == "401" || errorNum == "403") {
				launchLogin();
			} else {
				launchLogin();
			}
		}
	});
}


//
//
// TAKE IN DATA FROM LOGIN FORM
//
//

//
//
// FUNCTIONS FOR REPLY/ATTACH
//
//

// CLOSE REPLY FUNCTION
function closeReplyform (replytype,parentid) {
	var drawer = "#"+parentid+" div."+replytype+"div";
	$(drawer).animate({
		height: 0,
		overflow: 'hidden'
	}, 150, function() {
		$(drawer).html("").removeClass("opened");
	});
}

			
// OPEN REPLY FUNCTION
function openReplyform (replytype,parentid) {				
	// MAKE SURE BOTH ARE ALREADY CLOSED
	if ($("#"+parentid+" .replyinputdiv").hasClass("opened")) { closeReplyform("replyinput",parentid); $("a.commenttabs").removeClass("opened"); }
	
	// THEN SET UP AND OPEN THEM
	var contents = $("div#"+replytype+"form").html();
	var drawer = "#"+parentid+" div."+replytype+"div";
	
	$(drawer).animate({
		height: "100px",
		overflow: 'hidden'
	}, 150, function() {
		$(drawer).html(contents).addClass("opened");
		$(drawer).append('<a href="javascript:closeReplyform(\''+replytype+'\',\''+parentid+'\');" class="closereply">close</a>');
		var pkid = parentid.substr(8);
		
		if (replytype == "attach") {
			var postto = "/clipper/"+pkid+"/";
			$(drawer+ " form").attr("action",postto);
			
		} else {
			$(drawer+" form #id_in_reply_to").attr("value",pkid);
		}
		
	});
}

// ATTACH FUNCTIONS TO LINKS
function handleReplyform() {
	var parentid = $(this).closest("li.comment").attr("id");
	
	if ($(this).hasClass("attach")) { var replytype = "attach"; }
		else { var replytype = "reply"; }
						
	
	if ($("#"+parentid+" ."+replytype+"div").hasClass("opened")) {
		$(this).removeClass("opened");
		closeReplyform(replytype,parentid);
		return false;
	}
	openReplyform(replytype, parentid);
	$(this).addClass("opened");
	return false;
}

// Handle responses to questions (i.e. 'Me too!') links
function handleResponseLink() {
    var thiscomment = $(this).closest('.comment'); 
    var thiscomment_id = 
        thiscomment.attr('id').replace('comment-', '');
    var response_type = 'concur';

    $.ajax({
        type: "post", 
        url: "/api/json/comments/" + thiscomment_id + "/responses/",
        data: { type : response_type },
        success: function(data){
            // Update counter
            var count = thiscomment.children(".commentguts").children(".response-counter").children('.count');
            count_val = count.text();
            count_val++;
            count.text(count_val);
        },
        error: function (requestError, status, errorResponse) {
            var response_text = requestError.responseText;
            var response_data = $.parseJSON(response_text);
            var errorNum = requestError.status;

            if (errorNum == "401" || errorNum == "403") {
                var errorMsg = response_data.error; 
                // TODO: Prompt user to login
                thiscomment.append('<div class="error-message"><p>' + errorMsg + '</p><p class="instruction">(Click this box to close.)</p></div>');
                error_message = thiscomment.children('.error-message');
                error_message.css('display','block');

                $('.error-message').click(function() {
                    $(this).remove();
                });
            } 

        }
    });

    return false;
}
