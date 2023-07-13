###
# setwd("D://uyeda_lab/Projects/Evolution Simulator/Evolution Simulator/Code/shinyapp/EvoSim/")
###

# Import the required libraries
###############################
library(shiny)
library(ggtree)
library(ape)
library(shinythemes)
library(shinyBS)
library(shinyjs)
library(readxl)
library(DT)
library(data.table)
library(shinycssloaders)
library(ggplot2)
library(bslib)
library(shinydashboard)
library(cowplot)
library(sortable)
library(shinyjqui)
library(DiagrammeR)
library(htmltools)
library(ggimage)
# library(rgl)
# library(Rvcg)
# library(reticulate)
# library(r3js)
library(jsonlite)
###############################

# Import Elements
###############################
source("styling.R")
source("mainTab.R")
source("importData_ui.R")
source("editPlot.R")
source("editTable.R")
source("displayCodePanel.R")
source("plotButtons.R")
source("ggSideBar.R")
source("blendifyTab.R")
source("simulatedTraitsTab.R")
source("settingsMenu.R")
###############################


jsCode <- "shinyjs.changeModal = function() {
        $(document).off('focusin.modal');
    }"


# Define UI for application
ui <- fluidPage(

  tags$head(tags$script(HTML("
var modalClosedValue = 0;
$(document).on('hidden.bs.modal', '.modal', function (event) {
  if($(event.currentTarget).find('#plot2').length > 0) {
    modalClosedValue = modalClosedValue == 0 ? 1 : 0;
    Shiny.setInputValue('modalClosed', modalClosedValue);
  }
});
"))),
  #Dark theme for the app
  theme = bslib::bs_theme(version = 4, bootswatch = "darkly"),
  
  #import css styling
  styling_ui(),
  
  #right sidebar popup for editing plot elements
  ggSideBar_ui(),

  # Application title
  titlePanel("TraitBlender"),
  
  navbarPage(
    
    title = "",
    shinyjs::useShinyjs(),
    shinyjs::extendShinyjs(
      text = "
      $('#myModal').on('shown.bs.modal', changeModal());", 
      functions = c("changeModal")
                           ),
  
    mainTab_ui(),
        editPlot_ui(),
        editTable_ui(),
    blendifyTab_ui(),
    simulatedTraitsTab_ui(),
    settingsMenu_ui()
  )
)



# Server function
server <- function(input, output, session) {
  
  
  ### Checking that settings load properly
  if (file.exists("../data/settings/paths.json")) {
    # Read the JSON file
    paths <- jsonlite::fromJSON("../data/settings/paths.json")
  } else {
    # Create an empty JSON object
    paths <- list(blender = "")
  }
  
  
  # Create a reactive version of the paths object
  paths_reactive <- reactiveVal(paths)
  
  observe({
    updateTextInput(session, "blenderPath", value = paths_reactive()$blender)
  })
  
  observeEvent(input$blenderPath, {
    # Check if input$blenderPath is not empty
    if (nchar(input$blenderPath) > 0) {
      # Update the path for Blender
      paths <- paths_reactive()
      paths$blender <- input$blenderPath
      paths_reactive(paths)
      
      # Write the JSON object back to the file
      jsonlite::write_json(paths, "../data/settings/paths.json")
    }
  })
  
  
  
  
  
  # Main Page
  ##################################################################################
  
  # Import tree and character data
  #--------------------------------------------------------------------------------#
  data <- reactive({
    
    # If 'file1' is not uploaded, return a default empty table
    if (is.null(input$file1)) {
      return(data.frame(Label = rep("", 10), matrix(rep("", 90), ncol = 9, dimnames = list(NULL, paste0("C", 1:9)))))
    }
    
    # Ensure 'file1' is available
    req(input$file1)  
    
    # Determine the extension of the file
    ext <- tools::file_ext(input$file1$datapath)
    ext <- tolower(ext)  # Convert to lowercase for comparison
    
    # Error handling for Tabular Data import
    tryCatch({
      # Read the file based on its extension
      switch(ext,
             "csv" = read.csv(input$file1$datapath),
             "tsv" = read.delim(input$file1$datapath),
             "xls" = read_excel(input$file1$datapath),
             "xlsx" = read_excel(input$file1$datapath),
             "nexus" = {
               # Read the nexus file
               nexus_data <- ape::read.nexus.data(input$file1$datapath)
               
               # Convert the list to a data frame
               tip_names <- names(nexus_data)
               data_frame <- transpose(as.data.table(nexus_data))
               colnames(data_frame) <- paste0("C", 1:ncol(data_frame))
               data_frame <- data.table(Labels = tip_names, data_frame)
               data_frame
             },
             "nex" = {
               # Read the nexus file
               nexus_data <- ape::read.nexus.data(input$file1$datapath)
               
               # Convert the list to a data frame
               tip_names <- names(nexus_data)
               data_frame <- transpose(as.data.table(nexus_data))
               colnames(data_frame) <- paste0("C", 1:ncol(data_frame))
               data_frame <- data.table(Labels = tip_names, data_frame)
               data_frame
             },
             showNotification(paste0("Unsupported file type: .", ext), type = "error"))
    }, warning = function(w) {
      showNotification(paste0("Warning: ", w$message), type = "warning")
    }, error    = function(e) {
      showNotification(paste0("Error: ", e$message), type = "error")
    }, finally = {
      showNotification("Data loaded successfully!")
    })
  })
  phy <- reactive({
    req(input$file2)  # Ensure 'file2' is available
    
    # Error handling for Newick file import
    tryCatch({
      read.tree(input$file2$datapath)
    }, warning = function(w) {
      showNotification(paste0("Warning: ", w$message), type = "warning")
    }, error = function(e) {
      showNotification(paste0("Error: ", e$message), type = "error")
    })
  })
  #--------------------------------------------------------------------------------#
  
  # This stores the list of characters that make up the code that gets plotted
  #--------------------------------------------------------------------------------#
  source("code_vec.R")
  #--------------------------------------------------------------------------------#
  
  # Updates the values in code vec
  #--------------------------------------------------------------------------------#
  observeEvent(input$add_code, {
    new_code <- input$new_code
    current_code_vec <- unlist(code_vec())
    code_vec(c(current_code_vec, new_code))
  })
  #--------------------------------------------------------------------------------#
  
  # Collapses the code vec into one well-formatted string
  #--------------------------------------------------------------------------------#
  combined_code <- reactive({
    paste(unlist(code_vec()), collapse = " ")
  })
  #--------------------------------------------------------------------------------#
  
  # Renders the formatted code_vec string ('combined_code')
  #--------------------------------------------------------------------------------#
  output$code_display <- renderPrint({combined_code()})
  #--------------------------------------------------------------------------------#
  
  # Print the list buttons for the tree plot
  #--------------------------------------------------------------------------------#
  observeEvent(input$plot_elements, {
    output$ordered_items <- renderPrint({
      input$plot_elements
    })
  })
  #--------------------------------------------------------------------------------#
  
  # Track which plotting button was clicked last
  #--------------------------------------------------------------------------------#
  activePlottingButton <- reactiveVal(NULL) # Initialize the reactive variable
  
  for(i in 1:16) {
    local({
      j <- i
      observeEvent(input[[paste0("plot_button_", j)]], {
        if(is.null(activePlottingButton()) || activePlottingButton() != j) {
          activePlottingButton(j) # Update the reactive variable
        } else {
          activePlottingButton(NULL) # Set the variable to NULL
        }
      }, ignoreNULL = FALSE, ignoreInit = TRUE)
    })
  }

   observeEvent(input$modalClosed, {
     activePlottingButton(NULL)
   })
  #--------------------------------------------------------------------------------#
  
  
  # Opens the right sidebar when plot_button_1 is pressed
  #--------------------------------------------------------------------------------#
  observe({
  if(!is.null(activePlottingButton())) {
    shinyjs::runjs("$('#rightSidebar').addClass('open');") # Open the sidebar
  } else {
    shinyjs::runjs("$('#rightSidebar').removeClass('open');") # Close the sidebar
  }
  })
  
  #--------------------------------------------------------------------------------#
  
  # Tree plot on the main page
  #--------------------------------------------------------------------------------#
  output$plot1 <- renderPlot({
    # Check if a Newick file has been uploaded
    if (is.null(input$file2)) {
      # If not, display a blank plot with a grid
      ggplot() + 
        geom_hline(aes(yintercept = seq(-10, 10, by = 2.5)), color = "grey90") +
        geom_vline(aes(xintercept = seq(-10, 10, by = 2.5)), color = "grey90") +
        theme_void()
    } else {
      # If yes, plot the phylogenetic tree
      req(phy())  # Ensure 'phy' is available
      
      # Error handling for tree plotting
      tryCatch({
        eval(parse(text = combined_code()))
      }, warning = function(w) {
        showNotification(paste0("Warning: ", w$message), type = "warning")
      }, error = function(e) {
        showNotification(paste0("Error: ", e$message), type = "error")
      })
    }
  })
  #--------------------------------------------------------------------------------#
  
  # Tree plot on the 'edit plot' page
  #--------------------------------------------------------------------------------#
  output$plot2 <- renderPlot({
    # Check if a Newick file has been uploaded
    if (is.null(input$file2)) {
      # If not, display a blank plot with a grid
      ggplot() + 
        geom_hline(aes(yintercept = seq(-10, 10, by = 2.5)), color = "grey90") +
        geom_vline(aes(xintercept = seq(-10, 10, by = 2.5)), color = "grey90") +
        theme_void()
    } else {
      # If yes, plot the phylogenetic tree
      req(phy())  # Ensure 'phy' is available
      
      # Error handling for tree plotting
      tryCatch({
        eval(parse(text = combined_code()))
      }, warning = function(w) {
        showNotification(paste0("Warning: ", w$message), type = "warning")
      }, error = function(e) {
        showNotification(paste0("Error: ", e$message), type = "error")
      })
    }
  })
  #--------------------------------------------------------------------------------#

  # Table on the main page
  #--------------------------------------------------------------------------------#
  output$table1 <- DT::renderDataTable({
    req(data())  # Ensure 'data' is available
    datatable(data(), options = list(
      initComplete = JS(
        "function(settings, jsSon) {",
        "$(this.api().table().node()).css({'background-color': '#FFFFFF', 'color': '#000000'});",
        "$(this.api().table().body()).css({'background-color': '#FFFFFF', 'color': '#000000'});",
        "}"
      )
    ))
  })
  #--------------------------------------------------------------------------------#
  
  # Table on the 'edit table' page
  #--------------------------------------------------------------------------------#
  output$table2 <- DT::renderDataTable({
    req(data())  # Ensure 'data' is available
    datatable(data(), options = list(
      initComplete = JS(
        "function(settings, jsSon) {",
        "$(this.api().table().node()).css({'background-color': '#FFFFFF', 'color': '#000000'});",
        "$(this.api().table().body()).css({'background-color': '#FFFFFF', 'color': '#000000'});",
        "}"
      )
    ))
  })
  #--------------------------------------------------------------------------------#
  
  ##################################################################################
  
    
  # Blendify Page
  ##################################################################################
  #--------------------------------------------------------------------------------#
  # Initialize a reactive value to keep track of list items
  listItems <- reactiveVal(list())
  # Create a new list item when the 'addButton' is clicked
  observeEvent(input$addButton, {
    newListItems <- c(listItems(), paste0("Element ", length(listItems()) + 1))
    listItems(newListItems)
  })
  # Render the scrollable list
  output$scrollableList <- renderUI({
    div(id = 'scrollableList', style = 'overflow-y: auto; height: 200px; border: 1px solid; padding: 10px; border-radius: 15px;',
        lapply(listItems(), function(item) {
          div(item, style = "margin: 10px; padding: 10px; border: 1px solid; border-radius: 15px; cursor: pointer;", 
              onclick = paste0("alert('You clicked on: ", item, "');"))
        })
    )
  })
  #--------------------------------------------------------------------------------#
  ##################################################################################
  
  
  # Settings Page
  ##################################################################################
  #--------------------------------------------------------------------------------#
  observe({
    # Update CSS to change text size
    session$sendCustomMessage(type = 'jsCode',
                              list(js = paste0("$('body').css('font-size', '", input$text_size, "px');")))
    
    # Update CSS to change theme
    if (input$mode == "Dark") {
      session$sendCustomMessage(type = 'jsCode',
                                list(js = "$('body').css('background-color', 'black');
$('body').css('color', 'white');"))
    } else {
      session$sendCustomMessage(type = 'jsCode',
                                list(js = "$('body').css('background-color', 'white');
$('body').css('color', 'black');"))
    }
  })
  observe({
    
    # Update CSS to change text size
    session$sendCustomMessage(type = 'jsCode',
                              list(js = paste0("$('body').css('font-size', '", input$text_size, "px');")))
    
    # Update theme based on selected mode
    if (input$mode == "Dark") {
      shinyOptions(theme = shinytheme("darkly"))
    } else {
      shinyOptions(theme = shinytheme("flatly"))
    }
  })
  #--------------------------------------------------------------------------------#
  ##################################################################################

  
  
  ###SimulatedTraits page
  #--------------------------------------------------------------------------------#
  
    node_info <- reactiveVal(NULL)
  
    p <- reactive({
      ggtree(phy(), layout = "dendrogram") +  
        geom_tiplab() +
        theme_tree2(legend.position="none") +
        coord_cartesian(clip = 'off') +
        layout_dendrogram()
    })
  
    output$phy_tree <- renderPlot({
        req(p())
    })
    
    
    observeEvent(input$import_images_button, {
      
      print("Button pressed!")  # Debug print 1
      
      node_images <- list.files(path = "../node_images", pattern = "\\.(jpg|png)$", full.names = TRUE)
      print(node_images)  # Debug print 2
      
      node_info_data <- data.frame(
        node = as.integer(gsub("_.+$", "", basename(node_images))),
        image = node_images,
        stringsAsFactors = FALSE
      )
      
      print(node_info_data)  # Debug print 3
      
      node_info(node_info_data)
      
      plot_with_images <- p() %<+% node_info() + 
        geom_image(aes(image = image), nudge_x = -0.05)
      
      output$phy_tree <- renderPlot({
        plot_with_images
      })
    })
  #--------------------------------------------------------------------------------#
  
  #--------------------------------------------------------------------------------#
  #Blender interaction stuff#
    
    observeEvent(input$launchBlenderButton, {
      blender_path <- isolate(input$blenderPath)
      python_script_path <- normalizePath("../Python/gui.py")
      if (blender_path != "") {
        system2(blender_path, args = c("--python", shQuote(python_script_path)), wait = FALSE, invisible = FALSE)
      } else {
        print("No Blender path provided.")
      }
    })
    
    output$selected_file <- renderText({
      req(input$blender_executable)
      paste("You have selected: ", input$blender_executable$name)
    })
  #--------------------------------------------------------------------------------#
    
  #--------------------------------------------------------------------------------#
    # This keeps track of the .obj files that are stored in data/defaults via JSON in settings/predefined_meshes.JSON
    # Define a function to get the full paths of all .obj files in the ../data/defaults directory
    get_obj_files <- function() {
      # Get the full paths of all .obj files in the ../data/defaults directory
      obj_files <- list.files(path = "../data/defaults", pattern = "\\.obj$", full.names = TRUE)
      
      # Convert the relative paths to absolute paths
      obj_files <- sapply(obj_files, normalizePath)
      
      # Get the file names without extensions
      file_names <- basename(obj_files)
      file_names <- sub("\\.obj$", "", file_names)
      
      # Create a data frame where the first column is the file names and the second column is the paths
      obj_files_df <- data.frame(file = file_names, path = obj_files)
      
      # Convert the data frame to a list
      obj_files_list <- split(obj_files_df$path, obj_files_df$file)
      
      # Write the paths to a .JSON file
      jsonlite::write_json(obj_files_list, "../data/settings/predefined_meshes.json", pretty=TRUE)
    }
    
    # Create a reactive timer that invalidates every 1 second
    timer <- reactiveTimer(1000)
    
    # Use an observer to call get_obj_files every time the timer invalidates
    observe({
      # This line is necessary to register the dependency on the timer
      timer()
      
      # Call get_obj_files
      get_obj_files()
    })
    
     predefined_meshes <- reactiveFileReader(intervalMillis = 5000, session = session,
                                             filePath = "../data/settings/predefined_meshes.json",
                                             readFunc = jsonlite::fromJSON)
    
    # Store the current selection
    current_selection <- reactiveVal()
    
    
    # Watch for changes in the selected mesh
    observeEvent(input$meshSelect, {
      # Update the current selection
      current_selection(input$meshSelect)
      
      # Write the active mesh to the JSON file
      jsonlite::write_json(list(active_mesh = predefined_meshes()[[input$meshSelect]]), "../data/state/active_mesh.JSON")
    })
    
    observe({
      # Update the choices
      updateSelectInput(session, "meshSelect", choices = names(predefined_meshes()), selected = current_selection())
    })
    #--------------------------------------------------------------------------------#
    
    
    settings <- reactiveValues(paths = list(), predefined_meshes = list(), active_mesh = NULL)
    observeEvent(input$blenderPath, {
      # Check if input$blenderPath is not empty
      if (nchar(input$blenderPath) > 0) {
        # Update the path for Blender
        settings$paths$blender <- input$blenderPath
      }
    })
    # Define a function to get the full paths of all .obj files in the ../data/defaults directory
    get_obj_files <- function() {
      
      # Get the full paths of all .obj files in the ../data/defaults directory
      obj_files <- list.files(path = "../data/defaults", pattern = "\\.obj$", full.names = TRUE)
      
      # Convert the relative paths to absolute paths
      obj_files <- sapply(obj_files, normalizePath)
      
      # Get the file names without extensions
      file_names <- basename(obj_files)
      file_names <- sub("\\.obj$", "", file_names)
      
      # Create a data frame where the first column is the file names and the second column is the paths
      obj_files_df <- data.frame(file = file_names, path = obj_files)
      
      # Convert the data frame to a list
      obj_files_list <- split(obj_files_df$path, obj_files_df$file)
      # Update the predefined_meshes in settings
      settings$predefined_meshes <- obj_files_list
    }
    
    # Use an observer to call get_obj_files every time the timer invalidates
    observe({
      # This line is necessary to register the dependency on the timer
      timer()
      
      # Call get_obj_files
      get_obj_files()
    })
    # Watch for changes in the selected mesh
    observeEvent(input$meshSelect, {
      # Update the current selection
      current_selection(input$meshSelect)
      
      # Update the active_mesh in settings
      settings$active_mesh <- predefined_meshes()[[input$meshSelect]]
    })
    
    
    
    
}






# Run the application 
shinyApp(ui = ui, server = server)