/*
 * Javascript (mostly jQuery event handlers) for reporter/moderator 
 * functionality, including deleting topics, updating topic summaries, 
 * removing comment from a topic.
 *
 */

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

// DISASSOCIATE A COMMENT

function handleDisassociateCommentLink() {
    // Todo - hide children
    //
    var thiscomment_id = $(this).attr('id').replace('disassociatecommentlink-','');
    var thiscomment = $('#' + 'comment-' + thiscomment_id);
    var commentschildren = $('#' + 'comment-' + thiscomment_id + ' li');

    var curtopicid = $('.topicid').attr('id');
    $.ajax({
        type: "post", 
        url: "/disassociatecomment",
        data: { comment : thiscomment_id,
        topic : curtopicid},
        success: function(data){
            thiscomment.fadeOut();
            commentschildren.fadeOut();
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
    var thiscomment_id = $(this).attr('id').replace('deletecommentlink-','');
    var thiscomment = $('#' + 'comment-' + thiscomment_id);
    var commentschildren = $('#' + 'comment-' + thiscomment_id + ' li');

    $.ajax({
        type: "post", 
        url: "/deletecomments",
        data: { comments : thiscomment_id },
        success: function(data){
            thiscomment.fadeOut();
            commentschildren.fadeOut();
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
    // Get the id of the topic.  The parent div should have a class of
    // "topic" and and id of the form "topic-TOPIC_NUM".  So, we use
    // the jQuery selectors/attributes to get this and then use 
    // substr() to seperate the id number from the "topic-" part
    // of the id attribute.
    var topic = $(this).closest('.topic')
    var topicId = topic.attr('id').substr(6); 

    $.ajax({
        type: "delete",
        url: "/api/json/topics/" + topicId + "/",
        data: {},
        success: function(data) {
            // get handle to the tabs API (must have been constructed before this call)
            var api = $("ul.tabs").data("tabs");
            var tabIndex = api.getIndex();
            var numTabs = api.getTabs().length;

            if (tabIndex == 0) {
                // advance to the next tab
                api.next(); 
            }
            else {
                // advance to the previous tab
                api.prev(); 
            }

            tabIndex = api.getIndex(); // Get the new index

            topic.remove(); // Remove the topic wrapper div
            $(".switchtab#topic-" + topicId).remove(); // Remove the tab
            api.getPanes().hide().eq(tabIndex).show();

        },
        error: function (requestError, status, errorResponse) {
            var response_text = requestError.responseText;
            var errorNum = requestError.status;
            //var response_data = $.parseJSON(response_text);
            //var errorMsg = response_data['error'];
            // TODO: Handle this error somehow.

        }
    });

    return false;
}

// Show update summary form with default value
function handleUpdateTopicSummaryLink() {
    $('.update-topic-summary textarea').html($('.topic-summary').html());
    $('.update-topic-summary').show();
    return false;
}

// Hide the update summary form
function handleUpdateTopicSummaryCancel() {
    $('.topic-summary').show();
    $('.update-topic-summary').hide();
    return false;
}
   
// Update the summary
function handleUpdateTopicSummarySubmit() {
    // substr() to seperate the id number from the "topic-" part
    // of the id attribute.
    var topic = $(this).closest('.topic')
    var topicId = topic.attr('id').substr(6); 
    var newSummary = $(this).children('.new-topic-summary').html();

    $.ajax({
        type: "post",
        url: "/api/json/topics/" + topicId + "/summary/",
        data: { summary: newSummary },
        success: function(data) {
            topic.children('.topic-summary').html(newSummary);
            topic.children('.update-topic-summary').hide();
        },
        error: function (requestError, status, errorResponse) {
            var response_text = requestError.responseText;
            var errorNum = requestError.status;
            //var response_data = $.parseJSON(response_text);
            //var errorMsg = response_data['error'];
            // TODO: Handle this error somehow.

        }
    });

    return false;
}
