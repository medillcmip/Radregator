
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
        $('.replydiv form').unbind('submit', handleReplySubmit).bind('submit', handleReplySubmit);
		
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

// CREATE A NEW SOURCE

function handleNewSourceForm() {

    var sourcefirstname = $('#sourcefirstname').val();
    var sourcelastname = $('#sourcelastname').val();
    var sourceemail = $('#sourceemail').val();
    var sourcephone = $('#sourcephone').val();

    var sourceusername = sourcefirstname + sourcelastname;
    $.ajax({
        type: "post",
        url: "/api/json/users/",
        data: { username: sourceusername,
        password : 'password',
        email : sourceemail,
        phone : sourcephone,
        first_name : sourcefirstname,
        last_name : sourcelastname,
        dont_log_user_in : true,

        },
        success: function(data){
           // TK - Close Topic Form 
            location.reload(); // TODO - make this clearer
        },
        error: function (requestError, status, errorResponse) {
            var response_text = requestError.responseText;
            var response_data = $.parseJSON(response_text);
            var errorNum = requestError.status;

            var errorMsg = response_data['error'];// + response_data['error_html'];
            errorMsg += response_data['error_html'];
            $('#addsource').append('<div class="error-message"><p>' + errorMsg + '</p><p class="instruction">(Click this box to close.)</p></div>');
            error_message = $('#addsource').children('.error-message');
            error_message.css('display','block');

            $('.error-message').click(function() {
                $(this).remove();
            });

        }
    });

    
    return false;
    

}

// CREATE A NEW TOPIC
function handleNewTopicForm(){
    // Add a topic via Ajax
    var thissummary = $('#addtopicsummary').val();
    var thistitle = $('#addtopictitle').val();

    $.ajax({
        type: "post",
        url: "/newtopic/",
        data: { title : thistitle,
        summary_text: thissummary }


        ,
        success: function(data){
           // Close Topic Form 
            $('#addtopic').hide();
            location.reload(); // TODO - make this clearer
        },
        error: function (requestError, status, errorResponse) {
            var response_text = requestError.responseText;
            var response_data = $.parseJSON(response_text);
            var errorNum = requestError.status;

            var errorMsg = response_data['error'];
            $('#addtopic').append('<div class="error-message"><p>' + errorMsg + '</p><p class="instruction">(Click this box to close.)</p></div>');
            error_message = $('#addtopic').children('.error-message');
            error_message.css('display','block');

            $('.error-message').click(function() {
                $(this).remove();
            });

        }
    });

    
    return false;
}

function handleCommentSubmit(){
    var questionform = $('#questionform');
    var thiscomment_type = $('#questionform #id_comment_type_str').val();
    var thistext = $('#questionform #id_text').val();
    var thistopic = $('#questionform #id_topic').val();
    var thissources = $('#questionform #id_sources').val();
    var thisin_reply_to = '';

    $.ajax({
        type: "post",
        url: "/api/json/comments/",
        data: { in_reply_to : thisin_reply_to,
        topic: thistopic,
        comment_type_str : thiscomment_type,
        text : thistext,
        in_reply_to: thisin_reply_to,
        sources : thissources,


        },
        success: function(data){
        location.reload(); // TODO - make this clearer
            
        },
        error: function (requestError, status, errorResponse) {
            var response_text = requestError.responseText;
            var response_data = $.parseJSON(response_text);
            var errorNum = requestError.status;

            if (errorNum == "401") {
                // User isn't logged in
                var errorMsg = 'You need to <a class="login">login or register</a> to do this!' 
                questionform.append('<div class="error-message"><p>' + errorMsg + '</p><p class="instruction">(Click this box to close.)</p></div>');
                $('a.login').bind('click', launchLogin);
            } 
            else if (errorNum == "403") {
                // Another error
                var errorMsg = response_data.error; 
                questionform.append('<div class="error-message"><p>' + errorMsg + '</p><p class="instruction">(Click this box to close.)</p></div>');
            }

            error_message = questionform.children('.error-message');
            error_message.css('display','block');

            $('.error-message').click(function() {
                $(this).remove();
            });

        }
    });

    return false;
}


// HANDLE A REPLY
function handleReplySubmit(){
    var thiscomment = $(this).closest('.comment'); 
    var thiscomment_id = 
        thiscomment.attr('id').replace('comment-', '');

    var thisin_reply_to = thiscomment_id;
    var thistext = $('#id_text-'+thiscomment_id).val();
    var thiscomment_type = "3"; // Reply
    var thistopic = $("#id_topic-"+thiscomment_id).val();
    var this_sources = $('#id_sources-'+thiscomment_id).val();
    $('.replydiv form').unbind('submit', handleReplySubmit).bind('submit', handleReplySubmit);


    $.ajax({
        type: "post",
        url: "/api/json/comments/",
        data: { in_reply_to : thisin_reply_to,
        topic: thistopic,
        comment_type_str : thiscomment_type,
        text : thistext,
        in_reply_to: thisin_reply_to,
        sources : this_sources,


        },
        success: function(data){
        $('.replyform').hide();
        location.reload(); // TODO - make this clearer
            
        },
        error: function (requestError, status, errorResponse) {
            var response_text = requestError.responseText;
            var response_data = $.parseJSON(response_text);
            var errorNum = requestError.status;

            if (errorNum == "401") {
                // User isn't logged in
                var errorMsg = 'You need to <a class="login">login or register</a> to do this!' 
                thiscomment.append('<div class="error-message"><p>' + errorMsg + '</p><p class="instruction">(Click this box to close.)</p></div>');
                $('a.login').bind('click', launchLogin);
            } 
            else if (errorNum == "403") {
                // Another error
                var errorMsg = response_data.error; 
                thiscomment.append('<div class="error-message"><p>' + errorMsg + '</p><p class="instruction">(Click this box to close.)</p></div>');
            }

            error_message = thiscomment.children('.error-message');
            error_message.css('display','block');

            $('.error-message').click(function() {
                $(this).remove();
            });

        }
    });

    return false;


}

// DISASSOCIATE A COMMENT

function handleDisassociateCommentLink() {
    // Todo - hide children
    //
    var thiscomment = $(this).closest('.comment'); 
    var thiscomment_id = 
        thiscomment.attr('id').replace('comment-', '');

    var curtopicid = $("ul.tabs a.current").attr('id').replace('topic-', '');
    $.ajax({
        type: "post", 
        url: "/disassociatecomment",
        data: { comment : thiscomment_id,
        topic : curtopicid},
        success: function(data){
            thiscomment.fadeOut();
        },
        error: function (requestError, status, errorResponse) {
            var response_text = requestError.responseText;
            var response_data = $.parseJSON(response_text);
            var errorNum = requestError.status;
            

            if (errorNum == "401") {
                // User isn't logged in
                var errorMsg = 'You need to <a class="login">login or register</a> to do this!' 
                thiscomment.append('<div class="error-message"><p>' + errorMsg + '</p><p class="instruction">(Click this box to close.)</p></div>');
                $('a.login').bind('click', launchLogin);
            } 
            else if (errorNum == "403") {
                // User has already responded
                var errorMsg = response_data.error; 
                thiscomment.append('<div class="error-message"><p>' + errorMsg + '</p><p class="instruction">(Click this box to close.)</p></div>');
            }

            error_message = thiscomment.children('.error-message');
            error_message.css('display','block');

            $('.error-message').click(function() {
                $(this).remove();
            });

        }
    });

    return false;
}
    
// DELETE A COMMENT
function handleDeleteCommentLink() {
    // Todo - hide children
    //
    var thiscomment = $(this).closest('.comment'); 
    var thiscomment_id = 
        thiscomment.attr('id').replace('comment-', '');
    $.ajax({
        type: "post", 
        url: "/deletecomments",
        data: { comments : thiscomment_id },
        success: function(data){
            thiscomment.fadeOut();
        },
        error: function (requestError, status, errorResponse) {
            var response_text = requestError.responseText;
            var response_data = $.parseJSON(response_text);
            var errorNum = requestError.status;

            if (errorNum == "401") {
                // User isn't logged in
                var errorMsg = 'You need to <a class="login">login or register</a> to do this!' 
                thiscomment.append('<div class="error-message"><p>' + errorMsg + '</p><p class="instruction">(Click this box to close.)</p></div>');
                $('a.login').bind('click', launchLogin);
            } 
            else if (errorNum == "403") {
                // User has already responded
                var errorMsg = response_data.error; 
                thiscomment.append('<div class="error-message"><p>' + errorMsg + '</p><p class="instruction">(Click this box to close.)</p></div>');
            }

            error_message = thiscomment.children('.error-message');
            error_message.css('display','block');

            $('.error-message').click(function() {
                $(this).remove();
            });

        }
    });

    return false;
}

function handleCopyComment() {
    var thiscomment = $(this).closest('.comment'); 
    var thiscomment_id = 
        thiscomment.attr('id').replace('comment-', '');

    var thistopic = $(this).val();

    $.ajax({
        type: "post", 
        url: "/associatecomment",
        data: { comment : thiscomment_id,
        topic : thistopic }
        ,
        success: function(data){
            alert("Copied"); // Beautify me

        },
        error: function (requestError, status, errorResponse) {
            var response_text = requestError.responseText;
            var response_data = $.parseJSON(response_text);
            var errorNum = requestError.status;

            if (errorNum == "401") {
                // User isn't logged in
                var errorMsg = 'You need to <a class="login">login or register</a> to do this!' 
                thiscomment.append('<div class="error-message"><p>' + errorMsg + '</p><p class="instruction">(Click this box to close.)</p></div>');
                $('a.login').bind('click', launchLogin);
            } 
            else {
                // User has already responded
                var errorMsg = response_data.error; 
                thiscomment.append('<div class="error-message"><p>' + errorMsg + '</p><p class="instruction">(Click this box to close.)</p></div>');
            }
            

            alert(errorMsg);
            error_message = thiscomment.children('.error-message');
            error_message.css('display','block');

            $('.error-message').click(function() {
                $(this).remove();
            });

        }
    });

    return false;
}
// Flag a comment as opinion
function handleOpinionLink () {
    var thiscomment = $(this).closest('.comment'); 
    var thiscomment_id = 
        thiscomment.attr('id').replace('comment-', '');
    var response_type = 'opinion';
    
    $.ajax({
        type: "post", 
        url: "/api/json/comments/" + thiscomment_id + "/responses/",
        data: { type : response_type },
        success: function(data){
            // TK - Update counter
        },
        error: function (requestError, status, errorResponse) {
            var response_text = requestError.responseText;
            var response_data = $.parseJSON(response_text);
            var errorNum = requestError.status;

            if (errorNum == "401") {
                // User isn't logged in
                var errorMsg = 'You need to <a class="login">login or register</a> to do this!' 
                thiscomment.append('<div class="error-message"><p>' + errorMsg + '</p><p class="instruction">(Click this box to close.)</p></div>');
                $('a.login').bind('click', launchLogin);
            } 
            else if (errorNum == "403") {
                // User has already responded
                var errorMsg = response_data.error; 
                thiscomment.append('<div class="error-message"><p>' + errorMsg + '</p><p class="instruction">(Click this box to close.)</p></div>');
            }

            error_message = thiscomment.children('.error-message');
            error_message.css('display','block');

            $('.error-message').click(function() {
                $(this).remove();
            });

        }
    });

    return false;
}

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
            var count = thiscomment.children(".votebox").children(".count");
            count_val = count.text();
            count_val++;
            count.text(count_val);
        },
        error: function (requestError, status, errorResponse) {
            var response_text = requestError.responseText;
            var response_data = $.parseJSON(response_text);
            var errorNum = requestError.status;

            if (errorNum == "401") {
                // User isn't logged in
                var errorMsg = 'You need to <a class="login">login or register</a> to do this!' 
                thiscomment.append('<div class="error-message"><p>' + errorMsg + '</p><p class="instruction">(Click this box to close.)</p></div>');
                $('a.login').bind('click', launchLogin);
            } 
            else if (errorNum == "403") {
                // User has already responded
                var errorMsg = response_data.error; 
                thiscomment.append('<div class="error-message"><p>' + errorMsg + '</p><p class="instruction">(Click this box to close.)</p></div>');
            }

            error_message = thiscomment.children('.error-message');
            error_message.css('display','block');

            $('.error-message').click(function() {
                $(this).remove();
            });

        }
    });

    return false;
}

// Handler for logout (.logout) links
function handleLogoutLink() {
    FB.logout(function(response) {
    }); // Log the user out of Facebook

    // Return true so the browser follows the link (and logs the user out
    // of our site too)
    return true; 
}

// Handler for Facebook site login button.  This is the "fake" Facebook 
// login button that we show on the login page when a user is already
// logged into Facebook.
function handleFacebookSiteLoginButton() {
    var posturl = "/api/json/users/facebooklogin/";

    $.ajax({
        type: "post", context: $(this), url: posturl, data: {},
        success: function(data) {
            var loggeduser = data.username;
            parent.$("div.reglog").html("Hello, "+loggeduser+".  <a href='/logout'>Log out</a>");
            parent.$.fn.colorbox.close();
        },
        error: function (requestError, status, errorResponse) {
            var errorNum = requestError.status;
						
            errorMsg = jQuery.parseJSON(requestError.responseText).error;
            $(this).find(".errormsg").html(errorMsg);
            $(this).find(".errormsg").css("display", "block");
        }
    });

    return false;
}
