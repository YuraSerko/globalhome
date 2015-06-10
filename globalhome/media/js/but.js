$(function () {  
  $('a')   
    // create our new span.hover and loop through anchor:
    .append('<span class="hover" id="rsscolor"/>').each(function () {
      
      // cache a copy of the span, at the same time changing the opacity
      // to zero in preparation of the page being loaded
      var $span = $('> span.hover', this).css('opacity', 0);
      
      // when the user hovers in and out of the anchor
      $(this).hover(function () {
        // on hover
      
        // stop any animations currently running, and fade to opacity: 1
        $span.stop().fadeTo(300, 1);
      }, function () {
        // off hover
     
        // again, stop any animations currently running, and fade out
        $span.stop().fadeTo(300, 0);
      });
    });
});