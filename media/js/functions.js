var LOGIN_REQUIRED_MESSAGE = 'You need to login or <a href="/register/">register</a> to do this!'; 


// TOPIC DROP ON "ASK" FORM IN FOOTER
// Implement "ask" in footer (and header?)
function topicsDropShow() {
	$("#asktopicsdrop").css("display","block");
	//Character counter
	$("#askinput").charCount({
		allowed: 140,		
		warning: 20,
		counterText: 'Characters remaining: '	
	});
}


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



//callback to generate a shout out
//for news organizations that used 
//this site to drive the narrative of a
//story forward
function generateContributionCode(question_id){

	$.ajax({

		  type: "post", 
		  url: "/api_who_contributed/" + question_id + "/",
		 success: function(data){
			alert(data['user_list']);
		},
		 error: function (requestError, status, errorResponse) {
			var errorNum = requestError.status;
		    alert("error");	
		}
	});


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

/*
 * Set a flag so other javascript code can tell that a user is logged in.
 */
function setUserAuthenticated() {
    jQuery.data(document.body, "is_authenticated", true);
}

/* 
 * Is the user logged in?
 *
 * NOTE: This is likely to make authCheck() deprecated
 *
 */
function userIsAuthenticated() {
    // Read the flag set by setUserAuthenticated() to see if the user is
    // logged in
    return jQuery.data(document.body, "is_authenticated");
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
    if (userIsAuthenticated()) {
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
    else {
        displayMessage(LOGIN_REQUIRED_MESSAGE, 'error');
        return false;
    }
}

// GET TOPICS VIA API

function getTopics(){
    $.ajax({
        type: "get",
        url : "/api/json/topics/",
        data : {'result_type': 'popular', 'count': 5},
        success : function(data){
            $.each(data,function(index, topic)
            {
                var pk = topic.pk;
                var title = topic.fields.title;
                $('#toptopicslist').append("<li><a href='/topic/"+pk+"/'>"+title+"</a></li>");
            });
        },
        error: {
        // Show to user?
        }
    });

    $.ajax({
        type: "get",
        url : "/api/json/topics/",
        data : {'result_type': 'active', 'count': 5},
        success : function(data){
            $.each(data,function(index, topic)
            {
                var pk = topic.pk;
                var title = topic.fields.title;
                $('#activetopicslist').append("<li><a href='/topic/"+pk+"/'>"+title+"</a></li>");
            });
        },
        error: {
        // Show to user?
        }
    });
}

/**
 * Populate the footer "Top Questions" list using AJAX.
 * 
 */
function getTopQuestions() {
    $.ajax({
        type: "get",
        url : "/api/json/questions/",
        data : {'result_type': 'popular', 'count': '5'},
        success : function(data){
            $.each(data, function(index, question) {
                var topic_id = question.fields.topics[0]; 
                var text = question.fields.text;
                var comment_id = question.pk;
                $('#topquestionslist').append("<li><a href='/topic/"+ topic_id +
                                              "/#comment-" + comment_id +
                                              "'>"+text+"</a></li>");
            });
        },
        error: {
        // Show to user?
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
	 var thiscomment_id = $(this).attr('id').replace('replyform-','');
	 var thisform = $(this).attr('id');
	 var thisin_reply_to = thiscomment_id;
	 var thistext = $('#' + thisform + ' .clipper_text_field').val();
	 var thiscomment_type = "3"; // Reply
	 var thistopic = $("#id_topic-"+thiscomment_id).val();
	 var this_sources = $('#id_sources-'+thiscomment_id).val();
	 var this_url = $('#' + thisform + ' .clipper_url_field').val();

	 $('.replydiv form').unbind('submit', handleReplySubmit).bind('submit', handleReplySubmit);

		  if(this_url != '' &&  this_url != null){
				
				return true;
		  }
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
					 location.reload();
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

// Flag a comment as opinion
function handleOpinionLink () {
	 var thiscomment = $(this).closest('.comment'); 
	 var thiscomment_id = 
		  $(this).attr('id').replace('flagasopinion-', '');
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
					 var errorMsg = LOGIN_REQUIRED_MESSAGE; 
                     displayMessage(errorMsg, 'error');
				} 
				else if (errorNum == "403") {
					 // User has already responded
					 var errorMsg = response_data.error; 
                     displayMessage(errorMsg, 'error');
				}
		  }
	 });

	 return false;
}

function handleResponseLink() {
    var thiscomment = $(this).closest('.comment'); 
    var thiscomment_id = 
        $(this).attr("id").replace("thumbsup-","");
    var response_type = 'concur';

    $.ajax({
        type: "post", 
        url: "/api/json/comments/" + thiscomment_id + "/responses/",
        data: { type : response_type },
        success: function(data){
            // Update counter and tooltip
            var count = thiscomment.children(".votebox").children(".count");
            count_val = count.text();
            count_val++;
            count.text(count_val);
            if (thiscomment.hasClass("answer")) {
            	thiscomment.children(".votebox").attr("title","You've marked this as a good answer!");
            } else {
            	thiscomment.children(".votebox").attr("title","You've marked this as an important question!");
            }
			thiscomment.children(".votebox").tooltip({extraClass: "pretty", fixPNG: true, opacity: 0.95 });
        },
        error: function (requestError, status, errorResponse) {
            var response_text = requestError.responseText;
            var response_data = $.parseJSON(response_text);
            var errorNum = requestError.status;

            if (errorNum == "401") {
                // User isn't logged in
                var errorMsg = 'You need to login or <a href="/register/">register</a> to do this!' 
                displayMessage(errorMsg, 'error');
            } 
            else if (errorNum == "403") {
                // User has already responded
                var errorMsg = response_data.error; 
                displayMessage(errorMsg, 'error');
            }
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

/*
 * Hit the AJAX endpoint to try to log a Facebook user into the site or
 * automatically register them.
 *
 */
function authFacebookUserToSite() {
    var posturl = "/api/json/users/facebooklogin/";

    $.ajax({
        type: "post", context: $(this), url: posturl, data: {},
        success: function(data) {
            var loggeduser = data.username;
            location.reload();
        },
        error: function (requestError, status, errorResponse) {
            var errorNum = requestError.status;
                    
            errorMsg = jQuery.parseJSON(requestError.responseText).error;
            displayMessage(errorMsg, "error");
        }
    });
}

// Handler for Facebook site login button.  This is the "fake" Facebook 
// login button that we show on the login page when a user is already
// logged into Facebook.
function handleFacebookLoginButton() {
    FB.getLoginStatus(function(response) {
        if (response.session) {
            //console.debug("Facebook user found.  Try to authenticate them to this site.");
            authFacebookUserToSite();
        } else {
            //console.debug("No Facebook user found.  Launch Facebook login flow.");
            FB.login(function(response) {
                if (response.session) {
                    authFacebookUserToSite();
                }
                else {
                    // User cancelled Facebook login
                }
            });
        }
    });

    return false;
}

function getCurrentTopicId() {
	 topicId = $(".topicid").attr("id"); 

	 return topicId;
}


// Handle user sign-in form
// This handler grabs the form input and kills the behavior.
function handleUserSignInForm() {
	
    var thisuser = $("#usersignin-username").val();
    var thispass = $("#usersignin-password").val();

    //if (thisuer == '' || thispass == '')
    if (false)
    {
        // User didn't enter username or didn't enter password
        var errorMsg = 'You need to enter a user name and password.';
        displayMessage(errorMsg, 'error');
        return false;
    }
        

    // Clear prior error messages
    $('.errormsg').each(function(index) {
        $(this).html('');
    });

    var posturl = "/api/json/users/"+thisuser+"/login/";
        // alert(posturl);

    $.ajax({
        type: "post", context: $(this), url: posturl, data: { username: thisuser, password: thispass },
        success: function(data){
            var loggeduser = data.username;
            parent.$("div.reglog").html("Hello, "+loggeduser+".  <a href='/logout'>Not you</a>?");
            location.reload();
        },
        error: function (requestError, status, errorResponse) {
            var errorNum = requestError.status;
        
            var responseText = jQuery.parseJSON(requestError.responseText);
            var errorMsg = responseText.error;
            
            if(responseText.error_html)
            {
                errorMsg += responseText.error_html;
            }

            displayMessage(errorMsg, 'error');
        }
    });

    return false;

}

// MORE / LESS ON THREADS

// MORE / LESS ON CONTEXT

function contextexpander() {
	
	// GET TOTAL HEIGHT
	var fullheight = $("#context").height();
	//alert(fullheight);
	
	if (fullheight < 150) {
		$(".contextbot").css("display","none");
		return false;
	}
	
	// SET MINIMIZED HEIGHT ON LOAD
	var csschunk = {
      'height' : '10em',
      'overflow' : 'hidden'
    }
	$("#context").css(csschunk);
	
	// ADD CLICK-TO-TOGGLE
	$(".contextbot .expanderbut").toggle(
	function()
	{
		$('#context').animate({
		height: fullheight+10, 
		overflow: "auto",
		}, 500);
		$(".contextbot .more").css("display","none");
		$(".contextbot .less").css("display","block");
	},
	function()
		{
			$('#context').animate({
			height: "10em", 
			overflow: "hidden"
		}, 500);
		$(".contextbot .more").css("display","block");
		$(".contextbot .less").css("display","none");
	});
}


// Display a message in the message bar
function displayMessage(message, level) {
    level = typeof(level) != 'undefined' ? level : 'info';

    $('#messages p').html(message);
    $('#messageswrap').attr('class', level);
    $('#messageswrap').show();

}

// Hide the message bar
function hideMessages() {
    $('#messagewrap').hide();
}

// Set up earmarks on the answers (and other answer layout elements)
function earmarksetup() {
	$('.earmark').each(function(index) {
		var thisheight = $(this).closest(".answer").height();
		$(this).height(thisheight);
		
		// If "accepted"
		if ($(this).hasClass('accepted')) { $(this).children('.textspan').html('Accepted'); }
		
		// If "moderator"
		if ($(this).hasClass('moderator')) { $(this).children('.textspan').html('Moderator'); }

		// Get the "truthiness" and set background color accordingly
		var classstring = $(this).attr("class");
		var olevel = classstring.replace(/[a-zA-Z \-]/g, '');
		//console.log(olevel);		
		// SET HOW EACH OPINION DOWNVOTE WEIGHS ON THE COLORING
		var gval = 153 - (olevel * 30);

		var bground = "rgb(31,"+gval+",31)";
		
		$(this).css("background-color",bground);		
		
		
		// REMOVE THE MARGIN ON THE BOTTOM ANSWER
		$("ul.answers li:last div.comment").css("margin-bottom","0");
		
		
		// SET THE HEIGHT OF THE "CONNECTOR"
		var halfheight = (thisheight / 2);
		$(this).closest("li").children("div.aflag").height(halfheight).css("top",halfheight+"px");
		
		// REMOVE MARGIN FROM BOTTOM OF ANY ANSWERED QUESTIONS
		$("ul.answers li").has("ul.answers").children("div.comment").css("margin-bottom","0");
 	});
}

// REFRESH THE HEIGHT OF THE EARMARK
function earmarkrefresh(toggler) {
	var newheight = $(toggler).closest("div.comment").height();
	var newhalfheight = (newheight / 2);
	// alert(newheight);
	$(toggler).closest("div.comment").children("div.earmark").height(newheight);
	$(toggler).closest("li").children("div.aflag").height(newhalfheight).css("top",newhalfheight+"px");
}

// ANSWER/REPLY DRAWERS
function answerdrawers() {
	$('.replyformtoggle').click(function () {

                if (userIsAuthenticated()) {
                    var id = $(this).attr("id");
                    var formid = id.replace('toggle', '');
                    // Also toggle the link text
                    if ($(this).html() == "Reply") {
                        $(this).html("Hide this");
                    }
                    else {
                        $(this).html("Reply");
                    }
                    $('#' + formid).toggle();
                    // reset earmark+connector height
                    earmarkrefresh(this);
                }
                else {
                    displayMessage(LOGIN_REQUIRED_MESSAGE, 'error');
                }
                return false;
            });
            $('.answerformtoggle').click(function () {
                if (userIsAuthenticated()) {
                    var id = $(this).attr("id");
                    var formid = id.replace('toggle', '');

                    // Also toggle the link text
                    if ($(this).html() == "Answer this") {
                        $(this).html("Hide this");
                    }
                    else {
                        $(this).html("Answer this");
                    }
                    $('#' + formid).toggle();
                    earmarkrefresh(this);
                }
                else {
                    displayMessage(LOGIN_REQUIRED_MESSAGE, 'error');
                }

                return false;
            });
            $('.replyform').hide();
            $('.answerform').hide();
            $('#clipperform').hide();
}

function handleFavoriteCommentLink() {
    var thiscomment_id = $(this).attr('id').replace('favoritecommentlink-', '');
    var tag = '_favorite';
    alert(tag);
    
    $.ajax({
        type: "post",
        url: "/api/json/comments/tag/",
        data: { comment : thiscomment_id,
        tags: tag },
        success: function(data){
            
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

            error_message = thiscomment.children('.error-message');
            error_message.css('display','block');

            $('.error-message').click(function() {
                $(this).remove();
            });

        }
    });

    return false;
}

// SET UP "HIDE ANSWERS"
function hideanswers () {
	// IF THERE ARE ANSWERS, SHOW BUTTON
	$("ul.masterlist li").has("ul.answers").children("div.comment").children("div.qabox").children("p.userinfo").children("a.collapseanswers").css("display","inline");
	
	// THEN ARM BUTTON
	$("a.collapseanswers").click( function() {
		$(this).closest("li").children("ul.answers").slideToggle();
		if ($(this).html() == "Hide answers") {
			$(this).html("Show answers");
		}
		else {
			$(this).html("Hide answers");
		}
		return false;
	});
}




// RESIZABLE FONT ON HOMEPAGE AND ELSEWHERE
$.fn.fontfit = function(max) {
	var max_size = 50;
	if (typeof(max) == "undefined")
		max = max_size;
	$(this).wrapInner('<div id="fontfit"></div>');
	var dheight = $(this).height();
	var cheight = $("#fontfit").height();
	var fsize = (($(this).css("font-size")).slice(0,-2))*1;
	while(cheight<dheight && fsize<max) {
		fsize+=1;
		$(this).css("font-size",fsize+"px");
		cheight = $("#fontfit").height();
	}
	while(cheight>dheight || fsize>max) {
		fsize-=1;
		$(this).css("font-size",fsize+"px");
		cheight = $("#fontfit").height();
	}
	$("#fontfit").replaceWith($("#fontfit").html());
	return this;
}



//
//
// SET UP THE HOMEPAGE TIMELINE SLIDER
//
//

function initiateHomeTimeline() {
	var timeline = Raphael("timelinecontainer", 561, 36);
	var backdrop = timeline.rect(1, 1, 560, 26).attr("stroke-width","0");
	
	var slicecount = $("ul.featspotul li").length;
	var slices = new Array(slicecount);
	var segmentlength = (560 / slicecount);
	
	for(var i = 0; i < slicecount+1; i+=1) {  
		var multiplier = i * segmentlength;
		if (i % 2 == 0) {
			slices[i] = timeline.rect(multiplier - segmentlength, 0, segmentlength, 26).attr({fill: '#50b332'}).attr("stroke-width",0).attr("opacity",0.9);
		} else {
			slices[i] = timeline.rect(multiplier - segmentlength, 0, segmentlength, 26).attr({fill: '#50b332'}).attr("stroke-width",0).attr("opacity",0.8);
		}
		
		slices[i].hover(function () {
			this.attr({fill: "#007711"});
			this.node.style.cursor = 'pointer';  
		}, 
		function () {
			this.attr({fill: "#50b332"});
		});
		
		// CONNECT TIMELINE CLICKING TO HEADLINE SLIDER (& UPDATE THE "ANSWER THIS" LINK AND NODESTAMPS)
		slices[i].click(function () {
			// "SLIDE" THE MAIN SPOT
			var xfactor = this.attr("x");
			var slidevalue = -((xfactor/560)*(slicecount*961));
			$("ul.featspotul").animate({ left: slidevalue }, 600);
		
			// GET THE DATA FROM THE NEW LI CLASS AND UPDATE THE DIGITS
			var timelinestep = ((-slidevalue+961) / 961);
			updateDigits(timelinestep);
		
			// "SLIDE" THE ARROW
			var arrowanchor = xfactor + (segmentlength / 2) - 6;
			$("#timelinemarker").animate({ left: arrowanchor }, 600);
			
			// RESET THE TIMER
			clearInterval(countdown);			
		});
		
	}

	// Place the arrow initially and set initial digits
	var arrowstart = (segmentlength / 2) - 6;
	$("#timelinemarker").animate({ left: arrowstart }, 600);
	updateDigits(1);
}

function timedSlide() {
	// Set up the timer for rotation through the timeline
	// Get the current location
	var slicecount = $("ul.featspotul li").length;
	var segmentlength = (560 / slicecount);
	var timelineloc = $("#timelinemarker").css("left");
	timelineloc = parseInt(timelineloc.replace("px",""));
	var timelinestep = ((timelineloc + 6) + (segmentlength / 2)) / segmentlength;
	
	
	// Set up the new anchors values -- if the values exceed the width of the timeline, set back to first item
	var newtimelineloc = timelineloc + segmentlength;
	var newslidevalue = 0;
	if (newtimelineloc > 560) { newtimelineloc = (segmentlength / 2) - 6; } else { newslidevalue = -((timelinestep) * 961); }
	
	// Slide 'em and update digits
	$("#timelinemarker").animate({ left: newtimelineloc }, 600);
	$("ul.featspotul").animate({ left: newslidevalue }, 600);
	
	var newtimelinestep = ((newtimelineloc + 6) + (segmentlength / 2)) / segmentlength;
	updateDigits(newtimelinestep);
}

function initiateTimelineClock () {
	countdown = setInterval('timedSlide()',10000);
}

function updateDigits (timelinestep) {
	var classstrings = $("ul.featspotul li:nth-child("+timelinestep+")").attr("class").split(/\s+/);
	var classvals = new Array();
	classstrings.forEach(function(classstring) {
		var classpair = classstring.split("-");
		classvals[classpair[0]] = parseInt(classpair[1]);
	});
	
	// Grab the topic title (switch out for Ajax call later -- topicid unused now)
	function grabTopicName (topicid) {
		var topicname = $("ul.featspotul li:nth-child("+timelinestep+") span.topic-name").html();
		return topicname; 
	}
	
	// Add topic name to classvals array
	classvals["topicname"] = grabTopicName(classvals['topicid']);
	
	// Now write the values to the proper spots, shortening topic name when appropriate
	// options: answercount askcount topicid anchornum topicname
	
	$("ul.topicinfo li.answercount span").html(classvals['answercount']);
	$("ul.topicinfo li.askercount span").html(classvals['askcount']);
	
	if (classvals['topicname'].length > 14) {
		var topictext = classvals['topicname'].slice(0, 17).replace(/^\s+|\s+$/g,"");
		topictext = topictext + "...";
	} else {
		var topictext = classvals['topicname'];
	}
	
	$("ul.topicinfo li.topictitle span").html(topictext);
	$("ul.topicinfo li.topictitle").attr("title",classvals['topicname']).tooltip({extraClass: "pretty", fixPNG: true, opacity: 0.95 });
	
	// Last, update "Answer this" link and "Jump to topic"
	$("div.featinteractions a.answerthis").attr("href","/topic/"+classvals['topicid']+"/?answerthis=true&aanchor=comment-"+classvals['anchornum']);
	$("div.featinteractions a.topicpage").attr("href","/topic/"+classvals['topicid']);
}



function answerThisCheck() {
	// GET THE URL AND PARSE IT FOR BOTH GET PARAMS
	var $_GET = {};
	document.location.search.replace(/\??(?:([^=]+)=([^&]*)&?)/g, function () {
	    function decode(s) {
	        return decodeURIComponent(s.split("+").join(" "));
	    }
	    $_GET[decode(arguments[1])] = decode(arguments[2]);
	});
	
	if ($_GET["answerthis"] == "true") {
		var commentanchor = $_GET["aanchor"];
		$.scrollTo( 'li#'+commentanchor, 100, {offset: {top:-45, left:0} } );
		$('li#'+commentanchor+' a.answerformtoggle').click();
	}
}




//
//
// SET UP TIMELINE ON CONTENT PAGES
//
//

function initiateTopicTimeline() {
	var timeline = Raphael("timelinespot", 620, 200);
	var backdrop = timeline.rect(0, 0, 619, 150).attr("stroke-width","0").attr("fill","#323232");
	// COUNT THE NUMBER OF ANSWERS AND RETRIEVE IMPORTANT INFO (INCLUDING OPINION FLAGS)/STORE THEM IN ARRAY
	var answercount = $("ul.answers li").length;
	
	// THIS FUNCTION NEEDS TO BE REWRITTEN TO HIT THE BACKEND, NOT SCRAPE THE PAGE (SEE BELOW)
	var answerdata = grabAnswerData();



// FOR TESTING // 
/*
	answerdata["20060702"] = {author:"www.google.com",bgcolor:"rgb(10,110,10)",clip:"Here is what would be kind of a longer clip to show what would happen when that sort of thing occurred",date:"July 2",link:"http://www.washingtonpost.com",pageanchor:"comment-7",popularity:"1",source:"washingtonpost.com",title:"Here is the name of this article",year:"2006",month:"July"};
	
	answerdata = sortThisArray(answerdata);
*/
// END TESTING BLOCK //

//TESTING ISSUE 126 


//answerdata["20101217-1"] = {author: null,bgcolor: "rgb(31, 153, 31)",clip: null,date: "Dec. 17",link: undefined,month: "Dec.",pageanchor: undefined,popularity: "0",source: null,title: null,year: "2010"};
//doop, what?
//END TESTING ISSUE 126

	answerdata = sortThisArray(answerdata);


	// SET UP FUNCTION TO GET SIZE OF SLICES
	Object.size = function(obj) {
	    var size = 0, key;
	    for (key in obj) {
	        if (obj.hasOwnProperty(key)) size++;
	    }
		return size;
	};

	var itemcount = Object.size(answerdata);
	var segmentlength = (620 / itemcount);
	var slices = new Array(itemcount);
	var iterator = 0;
	var lastyear = "";
	var lastmonth = "";
	var lastday = "";
	
	//FIGURE OUT WHAT THE SCALE OF "THUMBS UP" IS
	var toppop = 0;
	for(var slicestamp in answerdata) {
		var thispop = parseInt(answerdata[slicestamp]["popularity"]);
		//console.log(thispop);
		if (thispop > toppop) { toppop = thispop; }
	}
	
	jQuery.each(answerdata, function(slicestamp, v) {
		
		var multiplier = iterator * segmentlength + segmentlength;
		var leftoffset = multiplier - segmentlength;
		
		
		// FIX HTML ISSUES
        try{
            var thistitle = answerdata[slicestamp]["title"].replace("&quot;","\"");
            var thistitle = thistitle.replace("&#8212;","-");
            var thistitle = thistitle.replace("&amp;","&");
		
            $('#prototype').clone().attr("id","slice"+slicestamp).appendTo('#tlhovercontainers');
            $('#slice'+slicestamp+' p.dateline').html(answerdata[slicestamp]["date"]+', '+answerdata[slicestamp]["year"]+'<a href="'+answerdata[slicestamp]["link"]+'" target="_blank">'+answerdata[slicestamp]["source"]+'</a>');
            $('#slice'+slicestamp+' h4.artheadline').html(thistitle);
            $('#slice'+slicestamp+' p.storyblurb a.articlelink').attr("href",answerdata[slicestamp]["link"]);
            if (answerdata[slicestamp]["clip"].length > 140) {
                var cliptext = answerdata[slicestamp]["clip"].slice(0, 140).replace(/^\s+|\s+$/g,"");
            } else {
                var cliptext = answerdata[slicestamp]["clip"];
            }
            $('#slice'+slicestamp+' p.storyblurb span').html(cliptext);
            

            var thisleftoffset = leftoffset;
            
            
            
            // NOW DRAW THE WHOLE DAMNED THING, INCLUDING DATES ALONG BOTTOM
            slices[slicestamp] = timeline.rect(leftoffset, 0, 2, 1).attr({fill: answerdata[slicestamp]["bgcolor"]}).attr("stroke-width",0).attr("opacity",0).attr("slicestamp",slicestamp);
            
            //DEAL WITH TEXT
            var thisyear = slicestamp.substring(0,4);
            var thismonth = slicestamp.substring(4,6); 
            var thisday = slicestamp.substring(6,8);
            
            if (thisyear != lastyear) {
                window["year" + thisyear] = timeline.text(leftoffset+2, 176, thisyear).attr({'text-anchor': 'start'}).attr({ "font-size": 15, "font-family": "Arial, Helvetica, sans-serif","font-weight": "bold", "color": "#323232" });
            }
            
            if (thismonth != lastmonth) {
                window["month" + thismonth] = timeline.text(leftoffset+2, 160, answerdata[slicestamp]["month"]).attr({'text-anchor': 'start'}).attr({ "font-size": 12, "font-family": "Arial, Helvetica, sans-serif", "color": "#323232" });			
            }
            
            //SAVE VALUES FOR NEXT ROUND
            lastyear = thisyear;
            lastmonth = thismonth;
            lastday = thisday;

            // var thisbarheight = (answerdata[slicestamp]["popularity"]+3)*10;
            // var thisbary = 150 - thisbarheight;
            var thisbarpop = answerdata[slicestamp]["popularity"];
            var thisbarheight = ((thisbarpop)*((150/toppop)))+24;
            var thisbary = 150 - thisbarheight;
                    
            //ANIMATE IN
            slices[slicestamp].animate({
                "20%": {y: thisbary},
                "40%": {opacity: 0.6},
                "50%": {height: thisbarheight},
                "80%": {opacity: 0.9},
                "100%": {width:segmentlength-1}
            }, 1500);
            
            
            // CONNECT HOVER TO HIDE/SHOW THE ARTICLES
            slices[slicestamp].hover(function () {
                this.attr("opacity",1);
                this.node.style.cursor = 'pointer';
                // $('#slice'+slicestamp).css("display","block").css("position","absolute").css("top",thisbary+(thisbarheight/2)+25).css("left",(thisleftoffset+(segmentlength/2))-150+"px");
                $('#slice'+slicestamp).css("display","block").css("position","absolute").css("top","160px").css("left",(thisleftoffset+(segmentlength/2))-150+"px");

            }, 
            function () {
                $('#slice'+slicestamp).css("display","none");
                this.attr("opacity",0.9);
            });
            
            $('#slice'+slicestamp).hover(function () { $(this).css("display","block"); }, function() { $(this).css("display","none"); });
            
            // CONNECT TIMELINE CLICKING LAUNCH NEW WINDOW WITH ARTICLE
            slices[slicestamp].click(function () {
                window.open(answerdata[slicestamp]["link"]);
            });
                
            iterator++;	

        }catch(e){}//not all articles have data populated 
	});
}


//NOTE: THIS FUNCTION NEEDS TO BE REWRITTEN TO HIT BACKEND FOR FULL ANSWER LIST...CURRENT IMPLEMENTATION ONLY READS WHAT'S ON PAGE
function grabAnswerData() {
	var answercount = $("ul.answers li").length;
	var answerdata = {};
	var iterator = 0;
	
	$("ul.answers li").each( function() {
		//NEED: title, clip, source, author, popularity, link, date, page anchor, bgcolor, year
		var thisanswerdata = {};		
		thisanswerdata["bgcolor"] = $(this).find("div.earmark").css("background-color");
		thisanswerdata["title"] = $(this).find("a.articlelink").html();
		thisanswerdata["clip"] = $(this).find("p.cliptext").html();
		thisanswerdata["source"] = $(this).find("a.publink").html();
		thisanswerdata["author"] = $(this).find("a.publink").html(); /* FIX THIS */
		thisanswerdata["link"] = $(this).find("a.publink").attr("href");
		thisanswerdata["popularity"] = $(this).find("p.count").html();
		thisanswerdata["pageanchor"] = $(this).find("a.answeranchor").attr("name");
		vartempdate = $(this).find("span.date").html().split(", ");
		thisanswerdata["date"] = vartempdate[0];
		thisanswerdata["year"] = vartempdate[1];
		
		
		// PUT TOGETHER THE DATE STAMP
		var datesplit = thisanswerdata["date"].split(" ");
		if (datesplit[1].length == 1) {
			datesplit[1] = "0"+datesplit[1];
		}
		var monthalone = datesplit[0];
		thisanswerdata["month"] = monthalone;
		
		var montharray = {"Jan.":"01","Feb.":"02","March":"03","April":"04","May":"05","June":"06","July":"07","Aug.":"08","Sept.":"09","Oct.":"10","Nov.":"11","Dec.":"12"}
		
		for (var val in montharray) {
    		var monthalone = monthalone.replace(val, montharray[val]);
		} 
		
		var dayalone = datesplit[1];
		var datestamp = thisanswerdata["year"] + monthalone + dayalone;
		
		
		// MAKE SURE NOTHING GETS OVERWRITTEN BY DOUBLING DATESTAMPS
		var iterator = 0;
		while (datestamp in answerdata)
		{
			iterator++;
			var breakstamp = datestamp.split("-");
			datestamp = breakstamp[0] + "-" + iterator;
		}
		
		answerdata[datestamp] = thisanswerdata;
	});
	answerdata = sortThisArray(answerdata);
	return answerdata;
}




function sortThisArray(arr){
	// Setup Arrays
	var sortedKeys = new Array();
	var sortedObj = {};

	// Separate keys and sort them
	for (var i in arr){
		sortedKeys.push(i);
	}
	sortedKeys.sort();

	// Reconstruct sorted obj based on keys
	for (var i in sortedKeys){
		sortedObj[sortedKeys[i]] = arr[sortedKeys[i]];
	}
	return sortedObj;
}

