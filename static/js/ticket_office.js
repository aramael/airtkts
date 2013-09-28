$(document).ready(function (){

    // Stripe Call
    Stripe.setPublishableKey('pk_test_TSQ7mAraIKeoGRhSUnFc8SI1');

    var steps = {
        1: $('.step-1'),
        information: $('.step-information'),
        guest: $('.step-guest-information'),
        payment: $('.step-payment-method'),
        pay: $('.step-payment'),
        4: $('.step-4')
    };

    function change_step(step_number){
        $('[class*=step-]:visible').transition('fade out');
        alert('EVERYTHING IS INVISIBLE: NOW SHOWING' + step_number);
        steps[step_number].transition('fade in');
    }

    var card = new Skeuocard($("#skeuocard"));
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
        payment_type_input.val($(this).attr('id')).trigger('blur');
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
            identifier : 'payment_type',
            rules:[{
                type   : 'empty',
                prompt : 'select a payment method'
            }]
        }
	},{
        inline: true,
        on: 'Blur',
        onSuccess: function(){

            var payment_method = steps['payment'].find('.form').form('get field', 'payment_type');
            if (payment_method.val() == 'credit'){
                change_step('pay');
                return;
            }

            change_step('thanks');
        }
    });

    $('form#airtkts').submit(function (e){
        if (card.isValid()){

            e.preventDefault();

            $(this).find('button').prop('disabled', true);

            Stripe.card.createToken({
                number: $('#cc_number').val(),
                cvc: $('#cc_cvc').val(),
                exp_month: $('#cc_exp_month').val(),
                exp_year: $('#cc_exp_year').val(),
                name: $('#cc_name').val()
            }, function (status, response){
                if (response.error) {

                    console.log(response.error.message);

                } else {
                    // token contains id, last4, and card type
                    var token = response['id'];

                    $('#stripeToken').val(token);

                    // Sever Side Validation of Credit Card Form

                }
            });
        }
    });

});