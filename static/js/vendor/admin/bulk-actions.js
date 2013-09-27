$(document).ready(function(){

    var allToggle = $('#action-toggle');
    var singleToggle = $('.action-select');
    var toggleCount = $('.selected-count');
    var checked_all = false;

    allToggle.change(function() {
        if(this.checked) {
            singleToggle.prop('checked', true);
            change_item_count(undefined, _max_bulk_item_count);
            checked_all=true;
        }else{
            singleToggle.prop('checked', false);
            change_item_count(undefined, 0);
            checked_all=false;
        }
    });

    singleToggle.change(function(){
        if(this.checked) {
            change_item_count();
        }else{
            change_item_count(-1);
            if (checked_all){
                allToggle.prop('checked', false);
                checked_all=false;
            }
        }
    });

    function change_item_count(increment, count){

        increment = typeof increment !== 'undefined' ? increment : 1;
        count = typeof count !== 'undefined' ? count : false;

        if (count == false && count !== 0){
            _current_bulk_item_count += increment;
        }else{
            _current_bulk_item_count=count
        }

        if (!checked_all && _current_bulk_item_count == _max_bulk_item_count){
            allToggle.prop('checked', true);
            checked_all=true;
        }

        toggleCount.text(String(_current_bulk_item_count))
    }

});