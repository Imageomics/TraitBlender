ggSideBar_ui <- function(){
  
  sections <- list(
    list(id = "1", title = "Labels", ui = div()),
    list(id = "2", title = "Theme", ui = div()),
    list(id = "3", title = "Scales", ui = div()),
    list(id = "4", title = "Panel", ui = div()),
    list(id = "5", title = "Legend", ui = div()),
    list(id = "6", title = "Code", ui = div(
      style = "overflow-y: auto; height: calc(100vh - 50px); z-index: 9092; position: absolute;",  # Set a higher z-index and position: relative
      textInput("new_code", "Enter new code here"),
      actionButton("add_code", "Add code"),
    )
    )
  )
  
  div(
    id = "rightSidebar",
    class = "bg-secondary",
    style = "position: relative;",  # Create a new stacking context
    div(
      id = "accordion",
      class = "accordion",
      lapply(sections, function(section) {
        div(
          class = "card",
          a(
            class = "btn btn-link d-block w-100 d-flex align-items-center",
            `data-toggle` = "collapse",
            `data-target` = paste0("#collapse", section$id),
            div(
              class = "card-header",
              id = paste0("heading", section$id),
              h2(
                class = "mb-0",
                style = "font-size: 14px;", 
                section$title
              )
            )
          ),
          div(
            id = paste0("collapse", section$id),
            class = "collapse",
            `aria-labelledby` = paste0("heading", section$id),
            `data-parent` = "#accordion",
            div(
              class = "card-body",
              section$ui  # Insert the UI components here
            )
          )
        )
      })
    )
  )
}
