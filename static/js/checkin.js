$(document).ready(function (){

    // ==============================================================================
    // Search Events
    // ==============================================================================

    function filter_results(query, section){
        $(".ticket").filter(function (){

            var parent = $(this).closest('li');

            if (query === ""){
                if (parent.hasClass('hide')){
                    parent.removeClass('hide');
                }
            }else{
                query = query.toLowerCase();

                if ($(".big",this).text().toLowerCase().indexOf(query) === -1) {
                    parent.addClass('hide');
                }
            }
        })
    }

    var search_input = $('.search input[type=search]');
    var current_target = null;

    search_input.clearSearch({linkText: ''});

    $(".search.overlay").click( function (event){
        $(this).hide(); // Hide the Overlay

        $(this).parents('header.search').addClass('active');

        // Focus on the Search Bar & Pull up Keyboard
        // Style the Search Bar while Searching
        search_input.focus().prop('placeholder','Search');

        // Remove Titlebar and Move Search to Top
        $('.titlebar').animate({height: 0}, {duration: 'fast', queue: false});
        $('.content.tickets').animate({'margin-top': 45}, {duration: 'fast', queue: false});
        $('header.search').animate({top: 0}, {duration: 'fast', queue: false});
    });

    $('.search.cancel').click(function (){
        // Hide Active Elements
        $(this).parents('header.search').removeClass('active');

        // Remove Search Bar Active Styling
        search_input.prop('placeholder','').val('').trigger('keyup');

        // Add Titlebar and Move Search to bottom
        $('.titlebar').animate({height: 44}, {duration: 'fast', queue: false});
        $('.content.tickets').animate({'margin-top': 90}, {duration: 'fast', queue: false});
        $('header.search').animate({top: 45}, {duration: 'fast', queue: false});
        $('.search.overlay').show();

    });

    var timeout;
    search_input.bind('textchange', function () {
        clearTimeout(timeout);
        var self = $(this);
        timeout = setTimeout(function () {
            filter_results(self.val());
        }, 500);
    });

    // ==============================================================================
    // Swipe Events
    // ==============================================================================

    var hammer = $('.tickets').hammer();

    hammer.on("dragstart dragend dragright", ".swipeable.ticket:not(.arrived):not(.declined)", function(event) {

        var parent = $(this).closest('li');
        var max_width = parent.innerWidth();
        var percent_swipe = event.gesture.deltaX/max_width;
        var action = 'unknown';

        // Current Action
        if (percent_swipe < 0.10){
            action = 'prepare'
        }else if (percent_swipe >= 0.10){
            action = 'execute'
        }

        if (event.type == 'dragstart'){
            current_target = event.currentTarget;
        }

        // =======================================
        // Process Finished Action
        // =======================================
        if (event.type == 'dragend'){

            if (current_target == event.currentTarget){
                if (action == 'prepare'){

                    $(this).animate({ "margin-left": 0 }, "slow" , function (){
                        parent.removeClass('prepare action');
                    });

                }else if (action == 'execute'){

                    var element = $(this);

                    $.post( _checkin_url, {'action': 'checkin', 'ticket': $(this).data('pk')}, function( data ) {
                        data = $.parseJSON(data);
                        if (data['success']){

                            var distance_left = max_width + 65 - parseFloat(element.css('margin-left'));

                            element.animate({ "margin-left": "+=" + distance_left + "px" }, "slow" , function (){
                                parent.animate({ "height": 0}, "slow", function (){
                                    parent.remove();
                                });
                            });
                        }else{
                            element.animate({ "margin-left": 0 }, "slow" , function (){
                                parent.removeClass('prepare action');
                                parent.removeClass('success');
                            });
                        }
                    });
                }
            }

            current_target = null;

        }

        // =======================================
        // Process Current Action
        // =======================================
        if (event.currentTarget == current_target){

            switch (action){
                case 'prepare':
                    parent.addClass('prepare action');
                    parent.removeClass('success');
                    break;
                case 'execute':
                    parent.removeClass('prepare action');
                    parent.addClass('success');
                    break;
                default:
                    break;

            }

            $(this).css('margin-left', event.gesture.deltaX);
        }

    });
});