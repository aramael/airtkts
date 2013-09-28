$(document).ready(function (){

    var steps = ['',
        $('.step-1'),
        $('.step-2'),
        $('.step-3'),
        $('.step-4')
    ];

    function change_step(step_number){
        $('[class*=step-]:visible').transition('fade out');
        steps[step_number].transition('fade in');
    }

    var ticket_type = $('.ticket-type');
    var payment_type = $('.payment-type');
    var ticket_type_input = $('#id_ticket_type');
    var payment_type_input = $('#id_payment_type');

    steps[1].click(function (){
        change_step(2);
    });

    ticket_type.add(payment_type).hover(function(){
        if(!$(this).hasClass('selected')){
            $(this).removeClass('tertiary');
            $(this).addClass('primary');
        }
    }, function (){
        if(!$(this).hasClass('selected')){
            $(this).removeClass('primary');
            $(this).addClass('tertiary');
        }
    });

    ticket_type.click(function (){
        $(ticket_type).each(function (){
            $(this).removeClass('teal selected');
            $(this).addClass('blue');
        });
        $(this).removeClass('blue');
        $(this).addClass('teal selected');
        ticket_type_input.val($(this).attr('id'));
    });

    payment_type.click(function (){
        $(payment_type).each(function (){
            $(this).removeClass('teal selected');
            $(this).addClass('blue');
        });
        $(this).removeClass('blue');
        $(this).addClass('teal selected');
        payment_type_input.val($(this).attr('id'));
    });



    steps[2].find('.form').form({
		firstName: {
			identifier  : 'first-name',
			rules: [{
				type   : 'empty',
				prompt : 'enter your first name'
			}]
		},
		lastName: {
			identifier  : 'last-name',
			rules: [{
				type   : 'empty',
				prompt : 'enter your last name'
			}]
		},
        ticket: {
            identifier : 'ticket_type',
            rules:[{
                type   : 'empty',
                prompt : 'select a ticket type'
            }]
        }
	},{
        inline: true,
        on: 'Blur',
        onSuccess: function(){
            change_step(3);
        }
    });

    steps[3].find('.form').form({
        ticket: {
            identifier : 'payment_method',
            rules:[{
                type   : 'empty',
                prompt : 'select a payment method'
            }]
        }
	},{
        inline: true,
        on: 'Blur',
        onSuccess: function(){
            change_step(4);
        }
    });

});