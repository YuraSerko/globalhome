jQuery(document).ready(function(){
	$("#iconbar").hover(
		function(){
			var iconName = $(this).find("img").attr("src");
			var origen = iconName.split("x.")[0];
			$(this).find("img").attr({src: "" + origen + "o.gif"});
			$(this).find("span").attr({
				"style": 'display:inline'
			});
			$(this).find("span").animate({opacity: 1, top: "-150"}, {queue:false, duration:400});
		}, 
		function(){
			var iconName = $(this).find("img").attr("src");
			var origen = iconName.split("o.")[0];
			$(this).find("img").attr({src: "" + origen + "x.gif"});
			$(this).find("span").animate({opacity: 0, top: "-130"}, {queue:false, duration:400, complete: function(){
								$(this).attr({"style": 'display:none'});
							}
						}
			);
		});
});

jQuery(document).ready(function(){
  $("#iconbar2").hover(
    function(){
      var iconName = $(this).find("img").attr("src");
      var origen = iconName.split("x.")[0];
      $(this).find("img").attr({src: "" + origen + "o.gif"});
      $(this).find("span").attr({
        "style": 'display:inline'
      });
      $(this).find("span").animate({opacity: 1, top: "-150"}, {queue:false, duration:400});
    }, 
    function(){
      var iconName = $(this).find("img").attr("src");
      var origen = iconName.split("o.")[0];
      $(this).find("img").attr({src: "" + origen + "x.gif"});
      $(this).find("span").animate({opacity: 0, top: "-130"}, {queue:false, duration:400, complete: function(){
                $(this).attr({"style": 'display:none'});
              }
            }
      );
    });
});

jQuery(document).ready(function(){
  $("#iconbar3").hover(
    function(){
      var iconName = $(this).find("img").attr("src");
      var origen = iconName.split("x.")[0];
      $(this).find("img").attr({src: "" + origen + "o.gif"});
      $(this).find("span").attr({
        "style": 'display:inline'
      });
      $(this).find("span").animate({opacity: 1, top: "-150"}, {queue:false, duration:400});
    }, 
    function(){
      var iconName = $(this).find("img").attr("src");
      var origen = iconName.split("o.")[0];
      $(this).find("img").attr({src: "" + origen + "x.gif"});
      $(this).find("span").animate({opacity: 0, top: "-130"}, {queue:false, duration:400, complete: function(){
                $(this).attr({"style": 'display:none'});
              }
            }
      );
    });
});

jQuery(document).ready(function(){
  $("#iconbar5").hover(
    function(){
      var iconName = $(this).find("img").attr("src");
      var origen = iconName.split("x.")[0];
      $(this).find("img").attr({src: "" + origen + "o.gif"});
      $(this).find("span").attr({
        "style": 'display:inline'
      });
      $(this).find("span").animate({opacity: 1, top: "-150"}, {queue:false, duration:400});
    }, 
    function(){
      var iconName = $(this).find("img").attr("src");
      var origen = iconName.split("o.")[0];
      $(this).find("img").attr({src: "" + origen + "x.gif"});
      $(this).find("span").animate({opacity: 0, top: "-130"}, {queue:false, duration:400, complete: function(){
                $(this).attr({"style": 'display:none'});
              }
            }
      );
    });
});


jQuery(document).ready(function(){
  $("#iconbar6").hover(
    function(){
      var iconName = $(this).find("img").attr("src");
      var origen = iconName.split("x.")[0];
      $(this).find("img").attr({src: "" + origen + "o.gif"});
      $(this).find("span").attr({
        "style": 'display:inline'
      });
      $(this).find("span").animate({opacity: 1, top: "-150"}, {queue:false, duration:400});
    }, 
    function(){
      var iconName = $(this).find("img").attr("src");
      var origen = iconName.split("o.")[0];
      $(this).find("img").attr({src: "" + origen + "x.gif"});
      $(this).find("span").animate({opacity: 0, top: "-130"}, {queue:false, duration:400, complete: function(){
                $(this).attr({"style": 'display:none'});
              }
            }
      );
    });
});

jQuery(document).ready(function(){
  $("#iconbar7").hover(
    function(){
      var iconName = $(this).find("img").attr("src");
      var origen = iconName.split("xsmall.")[0];
      $(this).find("img").attr({src: "" + origen + "osmall.PNG"});
      $(this).find("span").attr({
        "style": 'display:inline'
      });
      $(this).find("span").animate({opacity: 1, top: "-150"}, {queue:false, duration:400});
    }, 
    function(){
      var iconName = $(this).find("img").attr("src");
      var origen = iconName.split("osmall.")[0];
      $(this).find("img").attr({src: "" + origen + "xsmall.PNG"});
      $(this).find("span").animate({opacity: 0, top: "-130"}, {queue:false, duration:400, complete: function(){
                $(this).attr({"style": 'display:none'});
              }
            }
      );
    });
});

jQuery(document).ready(function(){
  $("#iconbar8").hover(
    function(){
      var iconName = $(this).find("img").attr("src");
      var origen = iconName.split("xsmall.")[0];
      $(this).find("img").attr({src: "" + origen + "osmall.PNG"});
      $(this).find("span").attr({
        "style": 'display:inline'
      });
      $(this).find("span").animate({opacity: 1, top: "-150"}, {queue:false, duration:400});
    }, 
    function(){
      var iconName = $(this).find("img").attr("src");
      var origen = iconName.split("osmall.")[0];
      $(this).find("img").attr({src: "" + origen + "xsmall.PNG"});
      $(this).find("span").animate({opacity: 0, top: "-130"}, {queue:false, duration:400, complete: function(){
                $(this).attr({"style": 'display:none'});
              }
            }
      );
    });
});
