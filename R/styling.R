styling_ui <- function(){
  
  tags$head(
    tags$style(HTML("
      .sidebar {
        height: 100vh;  /* vh is a CSS unit that stands for viewport height */
        overflow: auto;
      }

      .myActionButton {
        background-color: darkgrey;
        color: white;
        border: none;
        text-align: center;
        display: inline-block;
        font-size: 20px;
        padding: 4px 55px;
        margin: 5px 0px
      }

      .modal-backdrop {
          z-index: 1050 !important;
      }

      .modal {
          z-index: 1100 !important;
      }

      
      .myActionButton:hover {
        background-color: grey;
      }

      #rightSidebar {
        width: 0;
        height: 100%;
        position: fixed;
        z-index: 2;
        top: 0;
        right: 0;
        overflow-x: hidden;
        transition: 0.5s;
        padding-top: 60px;
        z-index: 9900;
      }

      #rightSidebar.open {
        width: 22.5%;
        transition: 0.5s;
      }
      
      .sidebar-div {
      position: relative;
      z-index: 9999;
    }
  ")),
    
    #this keeps track of the event of the bsModal with the tree plot on it closing, which is necessary
    #to make sure the sidebar closes when it closes
    tags$head(tags$script(HTML("
    var modalClosedValue = 0;
    $(document).on('hidden.bs.modal', '.modal', function (event) {
      if($(event.currentTarget).find('#plot2').length > 0) {
        modalClosedValue = modalClosedValue == 0 ? 1 : 0;
        Shiny.setInputValue('modalClosed', modalClosedValue);
      }
    });
  "))), 
    tags$script(HTML("
  $(document).on('shown.bs.modal', function() {
    $('#new_code').focus();
  });
")),
    tags$head(
      tags$script(HTML("
      $(document).on('shown.bs.modal', function() {
        $('.modal').css('pointer-events','none');
      });

      $(document).on('hidden.bs.modal', function() {
        $('.modal').css('pointer-events','auto');
      });
    "))
    )
    
    
    
    
  )
  
  
}