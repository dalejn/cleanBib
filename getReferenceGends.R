### First, manually create spreadsheet of first-/last-author first names
### One column, called "FA" will give first author names
### Another, called "LA" will give last author names

# set path to your cleaned .csv file
names=read.csv("/home/jovyan/cleanedBib.csv",stringsAsFactors=F)

# set path to working directory
setwd('/home/jovyan/')

# after registering for a gender-api free account, use your 500 free monthly 
# search credits by pasting your API key in the line below. You can find your
# key in your account's page https://gender-api.com/en/account/overview#my-api-key
genderAPI_key <- '&key=YOUR ACCOUNT KEY HERE'

require(rjson)
gendFA=NULL;gendLA=NULL
gendFA_conf=NULL;gendLA_conf=NULL

for(i in 1:nrow(names)){
  ### get probabilistic genders for the ith article from GenderAPI
  tfa=names$FA[i]
  tla=names$LA[i]
  
  json_file_fa=paste0("https://gender-api.com/get?name=",tfa,
                      genderAPI_key)
  json_data_fa=fromJSON(file=json_file_fa)
  
  ### Only query the server once if the first/last authors are the same
  if(tla!=tfa){
    json_file_la=paste0("https://gender-api.com/get?name=",tla,
                        genderAPI_key)
    json_data_la=fromJSON(file=json_file_la)
  }else{
    json_data_la=json_data_fa
    json_file_la=json_data_fa
  }
  
  ### Locate and save gender probabilities from json query
  if(json_data_fa$accuracy>=70){
    ### If probability is above 70%, assigned "W" or "M" to author
    gendFA[i]=ifelse(json_data_fa$gender=="female","W","M")
    gendFA_conf[i]=json_data_fa$accuracy
  }else{
    ### If not, assign "U" for unknown, and potentially fill these in manually
    gendFA[i]="U"
    gendFA_conf[i]=json_data_fa$accuracy
  }
  ### Do the same for last authors
  if(json_data_la$accuracy>=70){
    gendLA[i]=ifelse(json_data_la$gender=="female","W","M")
    gendLA_conf[i]=json_data_la$accuracy
  }else{
    gendLA[i]="U"
    gendLA_conf[i]=json_data_la$accuracy
  }
  
  ### Take a quick break before sending the server another request
  Sys.sleep(sample(1:2,1))
  print(i)
}

### Add new columns to data.frame to save for later use
names$FA_bin=gendFA; names$FA_conf=gendFA_conf
names$LA_bin=gendLA; names$LA_conf=gendLA_conf


### Pull names that the query server wasn't sure about
unknownFAs=names$FA[names$FA_bin=="U"]
unknownLAs=names$LA[names$LA_bin=="U"]
unknownFAs; unknownLAs

### At this stage, you can manually enter the gender of any
### if you can find pronouns or other signifiers online

# e.g. names$FA_bin[names$FA_bin=="Romy"]="W"


### Create column of gender categories (i.e., MM, WM, MW, WW)
names$GendCat=paste0(gendFA,gendLA)

# load manually modified results (OPTIONAL)
#names<-read.csv('Authors.csv')

##########################
# Tables and proportions #
##########################

#Get the overall counts and proportions for each category
table(names$GendCat)
round(table(names$GendCat)/sum(table(names$GendCat)),3)
tab1<- round(table(names$GendCat, exclude=c("MU", "UM", "UU"))*sum(table(names$GendCat))/
               sum(table(names$GendCat, exclude=c("MU", "UM", "UU"))),3)
tab1<- rbind(tab1, c(0.584*sum(table(names$GendCat)), 0.094*sum(table(names$GendCat)),
                     0.255*sum(table(names$GendCat)), 0.067*sum(table(names$GendCat))))

# Get proportions without unknowns
checkProportions <- round(table(names$GendCat, exclude=c("MU", "UM", "UU")))/sum(table(names$GendCat, exclude=c("MU", "UM", "UU")),3)

# Check gap between observed and expected
# Expected proportions in neuroscience were 58.4% for MM, 25.5% for WM, 9.4% for MW, and 6.7% for WW
checkProportions <- rbind(checkProportions, c(0.584, 0.094, 0.255, 0.067))
checkProportions
gap <- round((checkProportions[1,]-checkProportions[2,])*100/checkProportions[2,], 2)
gap

# Write
write.csv(names,"Authors.csv")
