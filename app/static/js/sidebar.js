/*!
 * Sidebar menu for Bootstrap 4
 * Copyright Zdeněk Papučík
 * MIT License
 */
(function($) {
  // Toggle sidebar menu
  $("#sidebar-toggle").on("click", function() {
    $("#wrapper").toggleClass("sidebar-toggle");
  });

  // List init
  $(".list-item").each(function() {
    $(this).parent().find(".link-arrow").addClass("up");
    if($(this).find(".link-current").length > 0) {
      $(this).parent().find(".link-current.link-arrow").addClass("active down");
      $(this).parent().find(".link-current").next(".list-hidden").show();
    }
  });

  // List open hidden
  $(".list-link").on("click", function() {
    $(this).parent().find(".link-arrow").toggleClass("active");
    $(this).next(".list-hidden").slideToggle("fast");
  });

  // List transition arrow
  $(".link-arrow").on("click", function() {
    $(this).addClass("transition");
    $(this).toggleClass("rotate");
    if($(this).parent().find(".link-arrow").hasClass("down")) {
      $(this).toggleClass("rotate-revert");
    }
  });
})(jQuery);