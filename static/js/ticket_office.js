$(document).ready(function (){

    var steps = {
        1: $('.step-1'),
        information: $('.step-information'),
        guest: $('.step-guest-information'),
        payment: $('.step-payment-method'),
        stripe: $('.step-payment'),
        4: $('.step-4')
    };

    function change_step(step_number){
        $('[class*=step-]:visible').transition('fade out');
        alert('EVERYTHING IS INVISIBLE: NOW SHOWING' + step_number);
        steps[step_number].transition('fade in');
    }

    var ticket_type = $('.ticket-type');
    var payment_type = $('.payment-type');
    var ticket_type_input = $('#id_ticket_type');
    var ticket_type_display = $('#ticket-choice');
    var payment_type_input = $('#id_payment_type');

    steps[1].click(function (){
        change_step('information');
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
        ticket_type_input.val($(this).attr('id')).trigger('blur');
        ticket_type_display.html($(this).find('.description').text());
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



    steps['information'].find('.form').form({
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

            if (steps['information'].find('.form').form('has field', 'guest_invited')){
                var guest_invited = steps['information'].find('.form').form('get field', 'guest_invited');
                if (guest_invited.is(':checked')){
                    change_step('guest');
                    return;
                }
            }

            change_step('payment');
        }
    });

    steps['guest'].find('.form').form({
		firstName: {
			identifier  : 'guest_first_name',
			rules: [{
				type   : 'empty',
				prompt : 'enter their first name'
			}]
		},
		lastName: {
			identifier  : 'guest_last_name',
			rules: [{
				type   : 'empty',
				prompt : 'enter their last name'
			}]
		},
        email: {
            identifier : 'guest_email',
            rules:[{
                type   : 'email',
                prompt : 'enter a valid email'
            }]
        }
	},{
        inline: true,
        on: 'Blur',
        onSuccess: function(){
            change_step('payment');
        }
    });

    steps['payment'].find('.form').form({
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
            $(this).closest('form').submit();
        }
    });

});