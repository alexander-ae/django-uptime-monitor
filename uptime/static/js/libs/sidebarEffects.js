/**
 * Inspirado en sidebarEffects.js de http://www.codrops.com
 */

function hasParentClass( e, classname ) {
	if(e === document) return false;

	if( $(e).hasClass(classname) ) {
		return true;
	}
	return e.parentNode && hasParentClass( e.parentNode, classname );
}

function init() {

	var container = $('#st-container'),
		button = document.getElementById('menu-btn'),

		resetMenu = function() {
			container.removeClass('st-menu-open');
			$(button).removeClass('close');
		},
		bodyClickFn = function(evt) {
			if( !hasParentClass( evt.target, 'st-menu' ) ) {
				resetMenu();
				document.removeEventListener( 'click', bodyClickFn );
			}
		};

	button.addEventListener( 'click', function( ev ) {
		ev.stopPropagation();
		ev.preventDefault();

		if ($(this).hasClass('close')) {
			$(this).removeClass('close');
			container.removeClass('st-menu-open');
		}
		else {
			$(this).addClass('close');
			container.className = 'st-container'; // clear
			container.addClass('st-effect-1');

			setTimeout( function() {
				container.addClass('st-menu-open');
			}, 25 );
			document.addEventListener( 'click', bodyClickFn );
		}
	});
}

init();
