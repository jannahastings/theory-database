library(readr)
# set wd (depending on computer)

# Iterate through each row of the dataframe
theory <- theory1
i <- 13
lucidchart <- function(theory){
  IDs <- list()
  theory <- theory[c(-1),]
  for (i in c(1:nrow(theory))) {
  name_value <- theory$Name[i]
  ID <- theory$Id[i]
  
  if (!(name_value %in% c("Text", "Process", "Line", "Page", "Block", "Rectangle"))) {
    # Identify all related Ids
    line_source <- unlist(theory[theory$Line.Destination == ID & !is.na(theory$Line.Source), 'Line.Source'])
    line_destination <- unlist(theory[theory$Line.Source == ID & !is.na(theory$Line.Destination), 'Line.Destination'])
    # Identify outcome line
    outcome_id <- line_destination[1]  # Assuming single outcome
    
    if (name_value == "Summing junction") {
      text_update <- "*"
    } else if (name_value %in% c("Merge", "Isoceles triangle")) {
      text_update <- "Type of"
    } else if (name_value == "Connector") {
      text_update <- "Kind of"
    } else if (name_value == "Or") {
      text_update <- "+"
    } 

    # Update Text Area 1
    theory$Text.Area.1[theory$Line.Destination == ID & !is.na(theory$Line.Destination)] <- text_update
    # Update relationships
    theory$Line.Destination <- ifelse(theory$Line.Destination == ID & !is.na(theory$Line.Destination), outcome_id, theory$Line.Destination)
    
    # Add ID to list
    IDs <- c(IDs, ID)
  }
  }

    # Remove fields that have become irrelevant
    theory <- theory[!theory$Id %in% IDs,]
    theory <- theory[!theory$Line.Source %in% IDs,]
    theory
    }




# List all files in the folder
folder_path <- "C:/Users/mabraun/OneDrive - Universität Zürich UZH/git/theory-database/theories"

files <- list.files(folder_path, full.names = TRUE)

for(x in files){
  file <- read.csv(x)
  file_processed <- lucidchart(file)
  file_name <- strsplit(x, "/")[[1]][8]
  write.csv(file_processed, paste0("C:/Users/mabraun/OneDrive - Universität Zürich UZH/git/theory-database/theories_processed/", file_name))
  }

theory1_path <- files[1]
theory1 <- read.csv(theory1_path)
lucidchart(theory1)
