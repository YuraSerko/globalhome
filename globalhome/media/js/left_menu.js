
		selected_news = $('#news_menu + ul li a').hasClass('selected')
		if(selected_news){
			$('#news_menu').addClass('down_arrow')
		}
		selected_near_you_menu = $('#near_you_menu + ul li a').hasClass('selected')
		if(selected_near_you_menu){
			$('#near_you_menu').addClass('down_arrow')
		}
		selected_finance_menu = $('ul.finance_menu li a').hasClass('selected')
		if(selected_finance_menu){
			$('#finance_menu').addClass('down_arrow')
		}
		selected_films = $('.clear_arrow li a').is('#films')
		selected_serials = $('.clear_arrow li a').is('#serials')

		if(selected_films || selected_serials){
			$('#video_menu').addClass('down_arrow')
		}
		selected_games = $('.games_menu + ul li a').hasClass('selected')
		if(selected_games){
			$('.games_menu').addClass('down_arrow')
		}

	