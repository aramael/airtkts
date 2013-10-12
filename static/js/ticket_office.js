var steps = {
    1: {
        title: 'Can You Attend?',
        handler: $('.step-1')
    },
    information: {
        title: '',
        handler: $('.step-information')
    },
    guest: {
        title: '',
        handler: $('.step-guest-information')
    },
    payment: {
        title: '',
        handler: $('.step-payment-method')
    },
    pay: {
        title: '',
        handler: $('.step-payment')
    },
    confirm: {
        title: '',
        handler: $('.step-confirm')
    },
    decline: {
        title: '',
        handler: $('.step-decline')
    }
};

function change_step(step_number){
    console.log('Changing to ');
    console.log(step_number);
    window.location.hash = step_number
}

$(document).ready(function (){

    // Bind an event to window.onhashchange that, when the hash changes, gets the
    // hash and adds the class "selected" to any matching nav link.
    $( window ).hashchange(function() {
        var hash = location.hash;

        hash = hash.replace( /^#/, "" ) || 1;

        // Set the page title based on the hash.
        document.title = steps[hash]['title'];

        $('[class*=step-]:visible').transition('fade out');
        steps[hash]['handler'].transition('fade in');
    });
    // Since the event is only triggered when the hash changes, we need to trigger
    // the event now, to handle the hash the page may have loaded with.
    $( window ).hashchange();

    // Stripe Call
    Stripe.setPublishableKey('pk_test_TSQ7mAraIKeoGRhSUnFc8SI1');

    var card = new Skeuocard($("#skeuocard"));
    var ticket_type = $('.ticket-type');
    var payment_type = $('.payment-type');
    var pay_later_price_display = $('#pay-at-door-price');
    var pay_now_price_display = $('#pay-now-price');
    var ticket_type_input = $('#id_ticket_type');
    var ticket_type_display = $('#ticket-choice');
    var payment_type_input = $('#id_payment_method');

    // Confrim Information
    var confrim_full_name = $('.invitee.full.name');
    var confrim_first_name = $('#first-name');
    var confrim_guest_full_name = $('#guest-full-name');
    var confrim_guest_first_name = $('#guest-first-name');
    var confrim_guest_email = $('#guest-email');
    var confrim_guest_note = $('#guest-note');
    var confrim_ticket_type = $('#ticket-type');
    var confrim_ticket_price = $('#ticket-price');
    var confrim_cc = $('#cc-last-four');
    var confrim_pay_now = $('#pay-now');
    var confrim_pay_later = $('#pay-at-door');
    var confrim_bring_guest = $('.bring.guest');

    $('#id_change_spelling_of_name').on( "click", function (){
       $('.invitee.information').toggleClass('hide');
   });

    $('.rsvp.attend').click(function (){
        change_step('information');
    });

    $('.rsvp.decline').click(function (){

        $.post(window.location, {rsvp:'DECLINED', first_name: $('#id_first_name').val(), last_name: $('#id_last_name').val(), email: $('#id_email').val()}, function (){

        });

        change_step('decline');
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

    steps['information']['handler'].find('.form').form({
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

            form = steps['information']['handler'].find('.form');

            // Fill Out Confirm Dialogue
            fname = form.form('get field', 'first_name').val();
            lname = form.form('get field', 'last_name').val();
            ticket_sale = form.form('get field', 'ticket_type').val();

            confrim_first_name.text(fname);
            confrim_full_name.text(fname + ' ' + lname);
            confrim_ticket_type.text(_available_tickets[ticket_sale]['name']);

            base_price = _available_tickets[ticket_sale]['price'];
            door_price = base_price + _door_surcharge;

            pay_now_price_display.text('$' + base_price.toString() +' USD');
            pay_later_price_display.text('$' + door_price.toString() +' USD');

            if (form.form('has field', 'guest_invited')){
                var guest_invited = form.form('get field', 'guest_invited');
                if (guest_invited.is(':checked')){
                    change_step('guest');
                    return;
                }
            }

            change_step('payment');
        }
    });

    steps['guest']['handler'].find('.form').form({
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

            window.guest_form = steps['guest']['handler'].find('.form');

            form = steps['guest']['handler'].find('.form');

            // Fill Out Confirm Dialogue
            fname = form.form('get field', 'guest_first_name').val();
            lname = form.form('get field', 'guest_last_name').val();
            email = form.form('get field', 'guest_email').val();
            note = form.form('get field', 'guest_note').val();

            console.log(form.form('get field', 'guest_first_name'));
            console.log(fname);

            confrim_guest_first_name.text(fname);
            confrim_guest_full_name.text(fname + ' ' + lname);
            confrim_guest_email.text(email);
            confrim_guest_note.text(note);
            confrim_bring_guest.removeClass('hide');

            change_step('payment');
        }
    });

    steps['payment']['handler'].find('.form').form({
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

            var payment_method = steps['payment']['handler'].find('.form').form('get field', 'payment_method');
            if (payment_method.val() == 'credit'){
                confrim_pay_now.removeClass('hide');
                confrim_ticket_price.text(pay_now_price_display.text());
                change_step('pay');
                return;
            }

            // Fill Out Confirm Dialogue
            confrim_pay_later.removeClass('hide');
            confrim_ticket_price.text(pay_later_price_display.text());

            change_step('confirm');
        }
    });

    steps['pay']['handler'].find('.submit').click(function (){
        if (card.isValid()){

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

                    $('#id_stripe_token').val(token);

                    num = $('#cc_number').val();
                    confrim_cc.text(num.substr(num.length - 4));

                    change_step('confirm');

                }
            });
        }
    });

});