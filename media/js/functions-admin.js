/*
 * Javascript (mostly jQuery event handlers) for reporter/moderator 
 * functionality, including deleting topics, updating topic summaries, 
 * removing comment from a topic.
 *
 */

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

// Delete a topic
function handleDeleteTopicLink() {
    return false;
}

// Show update summary form
function handleUpdateTopicSummaryLink() {
    return false;
}
