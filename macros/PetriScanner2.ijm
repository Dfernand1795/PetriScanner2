    //                    GNU GENERAL PUBLIC LICENSE
    //                       Version 3, 29 June 2007
    
    //Full license can be found in the PetriScanner directory.
    //Versioning history:
    //Edited last in June 5th.
    //User can now choose which plates to analyze instead of analyzing all of them.
    //Substituted constant DPI from 800 to read it from description file. 
    //Added variable mm = DPI/25.4, 
    //Changed px size of colonies (2200) to diameter (more intuitive).
    //Modifies verbose section, now shows elapsed times between important processes. 
    //Formatting - Fixed indentation issues and excess blank spaces.
    //Changed from Otsu to allow user to select their own thresholding methods.
    //Changed flag from “if (!Color_correction)" to "if (Color_correction)" - Line 308.
    //Changed macro's name from Growth_Analizer-SelectFolder to Growth_Analizer-Select_Experiment
    //Changed working on requested inputs for better comprehension.
    //Changed log output to more readable sentences. All outputs are separated by ":    " -two dots followed by four blank spaces. 
    
    
    ////////////////////////////////////////    GUI     /////////////////////////////////////////////////

    msg = "Welcome to PetriScanner    :)\nPlease select the options that fit better your analysis."
    msg_2  = "*Non-circular colonies bigger than 1.68 mm of diameter tend to be mistakenly segmented due to their form.\nIf your colonies are bigger than that, but are circular, please include a rough aproximation of their size\nin order to increase the tolerance to your colonies size.";
    msg_3 = "** Some colonies grow in patterns that are not shaped like circles (e.g. clover, flower like).\n  In this cases, watershed algorithm will separate each \"petal\" as its own colony if this option is marked. "
    Dialog.create("PetriScanner");
    T_Type_lis = newArray("Otsu","Huang","Intermodes","IsoData","Li","MaxEntropy","Mean","MinError","Minimum","Moments","Percentile","RenyiEntropy","Shanbhag","Triangle","Yen"); 
    
    Dialog.addMessage(msg);
    Dialog.addNumber("    Approx. colony app time (min):", 270);
    Dialog.addNumber("    Tolerance colony size* (mm):", 1.68);
    Dialog.addChoice("Thresholding type:", T_Type_lis);
    Dialog.addCheckbox("Correct background noise:    ", true);
    Dialog.addCheckbox("Subtract background color from colonies colors:    ", true); //Version V001 was set to true
    Dialog.addCheckbox("Verbose", true);
    Dialog.addCheckbox("Circular colonies**", true);
    Dialog.setInsets(0, 0, 0);
    Dialog.addHelp("https://imsb.ethz.ch/research/zampieri-group.html");
    Dialog.addMessage("Dishes to analyze:");
    Dialog.addCheckbox("1", true);
    Dialog.addCheckbox("2", true);
    Dialog.addCheckbox("3", true);
    Dialog.addCheckbox("4", true);
    Dialog.addCheckbox("5", true);
    Dialog.addCheckbox("6", true);
    Dialog.addMessage(msg_2);
    Dialog.addMessage(msg_3);
    Dialog.show();
        
    detect_t         = Dialog.getNumber();
    r_Avg_col_size   = Dialog.getNumber();
    T_Type           = Dialog.getChoice();
    Rmv_Bkgrnd = Dialog.getCheckbox();
    Color_correction = Dialog.getCheckbox();
    verbose          = Dialog.getCheckbox();
    watershed        = Dialog.getCheckbox();
    
    Selected_dishes = newArray(6);
    for (i = 0; i < 6; i++) {
        Selected_dishes[i] = Dialog.getCheckbox();
    };
    path = getDirectory("Select the experiment"); 
    path = replace(path, "Description.txt", "")

////////////////////////////////////////    Reading variables     /////////////////////////////////////////////////
    
    //1) Reading parameters from Description.txt
    filestring=File.openAsString(path+"Description.txt");
    rows=split(filestring, "\n");
    for(i=0; i<rows.length; i++){
        if (rows[i] != ""){
            columns=split(rows[i],"\t");
            if (columns[0] == "Interval:"){
                Interval = parseInt(columns[1]);
            };
            if (columns[0] == "Resolution:"){
                DPI = parseInt(columns[1]);
            };
            if (columns[0] == "White_Bkgrd:"){
                White_Bkground = split(columns[1], ",");
            };
            if (columns[0] == "Red_Colonies:"){
                Red_Cols = split(columns[1], ",");
            };
        };
    };
    run("Set Measurements...", "area mean stack standard center bounding integrated redirect=None decimal=9");
    for (Dish = 1; Dish < 7; Dish++){
        if(Selected_dishes[Dish-1] == 1){
            //1.1) Declaring variables for experiment:
            Threshold    = round(detect_t/Interval);
            Red_Col      = parseInt(Red_Cols[Dish-1]);
            White_Bkgrn  = parseInt(White_Bkground[Dish-1]);
            //1.1.1) String formating
            if (Dish == 1){
                Red_Col      = parseInt(substring(Red_Cols[Dish-1], 1, 2));
                White_Bkgrn  = parseInt(substring(White_Bkground[Dish-1], 1, 2));
            };
            if (Dish == 6){
                Red_Col      = parseInt(substring(Red_Cols[Dish-1], 0, 1));
                White_Bkgrn  = parseInt(substring(White_Bkground[Dish-1], 0, 1));
            };
            //1.2) Printing parameters for log file.
            //If there is a log file open, close it. 
            if (isOpen("Log")){
                close("Log");
            }
            if (verbose){
                //Parameters read from command line
                print("Subtract background color from colonies colors:    " +Color_correction);
                print("Correct background noise:    "       + Rmv_Bkgrnd);
                print("Circular colonies:    "              + watershed);
                print("Approx. colony app time (min):    "    + detect_t);
                print("Average colony size:    "            + r_Avg_col_size);
                print("Subtracted frames:    "             + Threshold);
                print("Threshold type:    "                 + T_Type);
                //Parameters read from Description file
                print("Scanning interval:    "              + Interval);
                print("DPI of scan:    "                   + DPI);
                print("TTC salts (red colonies):    "       + Red_Col      );
                print("White Background:    "               + White_Bkgrn  );
                print("Path to images:    "                 + path+"Images\\"+Dish);
                };
            mm = DPI/25.4;
            Avg_col_size = r_Avg_col_size * mm;
            Avg_col_size = (Avg_col_size*0.5)*(Avg_col_size*0.5)*3.1416;
            if (verbose){
                print("Px size: "+Avg_col_size);
                Time = getTime();
                print("Description file read successfully.\nLoading images...");
            };
            //Opening images
            run("Image Sequence...", "open="+path+"/Images/"+Dish+"/"+Dish+"-1.tif sort");
            //Removing previous 
            run("Set Scale...", "distance=0 global");
            rename("Unaltered_Color");
            //Adjusting variables to work with current DPI settings.
            print("Number of images in dataset:    "+nSlices);
            if (verbose){
                print("Time elapsed to load images from dish "+Dish+":    "+(getTime()-Time)+" ms");  
            };      
            
////////////////////////////////////////    Image Processing /////////////////////////////////////////////////
            if (verbose){
                Time = getTime();
            };
            //2 Removing dust particles
            run("Remove Outliers...", "radius="+floor(DPI/100)+" threshold=10 which=Bright stack"); 
            if (verbose){
                print("Image processing time (exclusively removing outliers):    "+(getTime()-Time)+" ms");  
            };           
            //2.2) Subtracting white (background - 255,255,255) from signal (x,x,x) is impossible -result will be 0 or negative- therefore we have to invert the stack coloration.
            if (White_Bkgrn){       // White background.
                run("Invert", "stack");
            };
             //""Unaltered_Color" will be the image where colors are going to be calculated.
            run("Duplicate...", "title=tmp duplicate");             
            //Depending on the experimental setup, we need to adjust some parameters.
            if (!White_Bkgrn){              //[White|Red] colonies, w/ black background.
                selectWindow("tmp");
                run("Split Channels");
                close("tmp (blue)");
                close("tmp (green)");
                selectWindow("tmp (red)");          //Red signal has the less noise when the background is black.
                rename("WorkingImage");
            };
            if (White_Bkgrn){   // Red colonies, w/ white background. (White colonies are invisible in white background
                selectWindow("tmp");
                run("Split Channels");
                close("tmp (red)");
                close("tmp (blue)");
                selectWindow("tmp (green)");    //Green signal has the less noise when the background is White.
                rename("WorkingImage");
                run("Duplicate...", "title=tmp duplicate range=1-"+Threshold);
                run("Z Project...", "projection=[Max Intensity]");
                close("tmp");
                imageCalculator("Subtract stack", "WorkingImage" ,"MAX_tmp");
                close("MAX_tmp");   
            };
///////////////////////////////////////    Segmentation    ///////////////////////////////////////////////////////////////

            //3.1) Obtaining the outline of a given colony.
            //Gaussian Blur removes individual pixel noise.
            //Standard deviation favors the change in px intensities of growing colonies, increasing colony signal (except for the edges).
            run("Duplicate...", "title=To_Mask duplicate");
            run("Gaussian Blur...", "sigma=3 stack");
            run("Z Project...", "projection=[Standard Deviation]");
            run("8-bit");
            //Grayscale or Binary watershed.
            //Big colonies tend to be falsely segmented when using grayscale watershed due to darker spots inside the colonies. 
            //To solve this, we correct by measuring the size of the colonies near the center where we assume there is little to no noise from the 
            //edges of the plate.   
            selectWindow("To_Mask");
            setSlice(nSlices);
            makeOval(getWidth*0.1, getWidth*0.1, getWidth*0.8, getWidth*0.8); //Small section in the center of the plate.
            run("Duplicate...", "title=tmp");
            run("Clear Outside");
            selectImage("tmp");
            setAutoThreshold(T_Type+" dark");             
            run("Convert to Mask");
            run("Options...", "iterations=2 count=1 black do=Open");
            run("Watershed");
            run("Analyze Particles...", "show=Masks display clear in_situ");
            close("tmp");
            //3.1.2) Measuring Average particle size - Reading results table to observe the average particle size.
            headings = split(String.getResultsHeadings);
            Sizes = 0;
            for (col=0; col<lengthOf(headings); col++){
                if (headings[col] == "Area"){
                     for (row=0; row<nResults; row++) {
                        Sizes += getResult(headings[col],row);
                    };
                };
            };
            //Particle Average:
            Size_Avg = (Sizes/nResults);
            selectWindow("STD_To_Mask");
            print("Average colony size:    "+ (sqrt(Size_Avg/3.1416)*2)/mm);
            //If colonies are small:
            //we use grayscale watershed from MorphoLibJ, since it's more sensitive to px intensities.
            if (Size_Avg < Avg_col_size){       
                print("Type of watershed:    Grayscale");
                run("Invert");
                if (White_Bkgrn){
                    //Red colonies have a bigger amount of noise in their measurements. In consequence, we decrease the detection threshold.
                    run("Classic Watershed", "input=STD_To_Mask mask=None use min=0 max=160");
                };
                if (!White_Bkgrn){
                    run("Classic Watershed", "input=STD_To_Mask mask=None use min=0 max=200");
                };
                run("8-bit");
                setThreshold(1, 255);
                run("Convert to Mask");
           };
            //If colonies are Big:
            //perform a common binary watershed. This is driven by the shape of the colony and ignores px intensities since it only works with binary images.
            else{
                print("Type of watershed:    Binary");
                setAutoThreshold(T_Type+" dark");             
                run("Convert to Mask");
                run("Options...", "iterations=2 count=1 black do=Open");
                run("Watershed");
            };
            rename("OuterMask");
            close("STD_To_Mask");
            close("To_Mask");
            //3.2) Here we increased the outer mask by 1 to avoid losing information. Since we are working with the standard deviation of the images
            //we are most likely losing the information of the outer section.
            run("Duplicate...", "title=tmp");
            run("Close-");
            imageCalculator("Difference create", "tmp","OuterMask");
            selectWindow("Result of tmp");
            run("Invert");
            rename("Septums");
            close("tmp");
            selectWindow("OuterMask");
            run("Options...", "iterations=2 count=1 black do=Dilate");
            imageCalculator("AND", "OuterMask","Septums");
            run("Watershed");
            close("Septums");
            //3.3) Light Correction in the WorkingImage
            // Correction in white background images is performed in 2.3. This step has no effect on the white images since 
            // all pixel values have been already removed.
            selectWindow("WorkingImage");
            if (!White_Bkgrn){
                run("Enhance Contrast...", "saturated=2 normalize equalize process_all use");
            };
            run("Gaussian Blur...", "sigma=1 stack");
            run("Duplicate...", "title=noise duplicate range=1-"+Threshold);
            run("Z Project...", "projection=[Max Intensity]");
            run("Smooth");
            close("noise");     
            imageCalculator("Subtract create stack", "WorkingImage","MAX_noise");
            close("MAX_noise");
            //3.4) Creating mask per each frame.
            run("Gaussian Blur...", "sigma=3 stack");
            run("Convert to Mask", "method="+T_Type+" background=Dark calculate black stack");
            rename("Final_Mask");
            //If we are working with an irregular shaped colony (e.g. Leaf-shaped, star-shaped, non-circular) 
            //the watershed algorithm would segment it. If this were true, we need to mark as false the watershed option 
            if (watershed){
                imageCalculator("AND stack", "Final_Mask","OuterMask");
            };
            else {
                run("Options...", "iterations="+floor(DPI/200)+" count=1 black do=Open stack");
                run("Analyze Particles...", "  show=Masks clear include in_situ stack");
            };
            close("OuterMask");
            close("WorkingImage");
            //3.5) Remove all detected particles that are not present in the region of interest of the last fame.
            setSlice(nSlices);
            run("Duplicate...", "title=Last_Frame");
            imageCalculator("AND stack", "Final_Mask","Last_Frame");
            close("Last_Frame");
            //3.6) Create the labels for colony - Ids that will be used in the future. 
            selectImage("Final_Mask");
            run("Reverse");
            run("Connected Components Labeling", "connectivity=6 type=[16 bits]");
            rename("Labeled_Colonies");
            selectImage("Unaltered_Color");
            run("Reverse");
            //3.7) Remove noise and background color from the unaltered image - If we were to want to measure the observed colors, we should mark the signal flag as false. 
            //Nevertheless, we are interested in the change of coloration with respect of the background, therefore, subtracting the background intensities is the default.
            if (Color_correction){
                selectImage("Unaltered_Color");
                run("Duplicate...", "title=tmp duplicate range="+nSlices-Threshold+"-"+nSlices);
                run("Z Project...", "projection=[Max Intensity]");
                close("tmp");
                imageCalculator("Subtract stack", "Unaltered_Color" ,"MAX_tmp");
                close("MAX_tmp");
            };
            rename("To_Calculate");
            if (verbose){
                print("Image processing time for dish "+Dish+":    "+(getTime()-Time)+" ms");  
                Time = getTime(); // Start timer for the section responsible to measure values .
            };      

            //4)Measuring colony morphology and color.
            run("Set Scale...", "distance="+DPI+" known=25.4 unit=mm global");  //4.1) Setting appropriate DPI scale:

            //4.3) Measure Grayscale values and their shape attributes.

            /////////////////////////////////////////////////////////   New section   //////////////////////////////////////////////////
            // With this section we generate images that show the quality of the segmentation at the last point, for them to qualitatively asses quality. 
            selectImage("To_Calculate");
            setSlice(1);
            run("Duplicate...", "title=Last_frame");
            selectWindow("Final_Mask");
            setSlice(1);
            run("Duplicate...", "title=Last_frame_mask");
            run("Analyze Particles...", "  show=Nothing clear  add");
            selectWindow("Last_frame");
            run("From ROI Manager");
            run("Flatten");
            run("Scale Bar...", "width=10 height=10 font=56 color=Yellow background=None location=[Lower Left] bold overlay");
            run("Flatten");
            selectWindow("Last_frame");
            run("Scale Bar...", "width=10 height=10 font=56 color=Yellow background=None location=[Lower Left] bold overlay");
            if  (!File.exists(path+"/Raw_csv_results/")){
                File.makeDirectory(path+"/Raw_csv_results/");
            };
            if  (!File.exists(path+"/Raw_csv_results/"+Dish)){
                File.makeDirectory(path+"/Raw_csv_results/"+Dish);
            };
            saveAs("Tiff", path+"/Raw_csv_results/"+Dish+"/Last_frame_overlay.tif");
            close("Last_frame-1");
            close("Last_frame");
            close("Last_frame_mask");
            selectWindow("Last_frame-2");
            saveAs("Tiff", path+"/Raw_csv_results/"+Dish+"/Last_frame_flattened.tif");
            close("Last_frame-2");
            // End of the section.
            
            selectWindow("Final_Mask");
            run("Set Measurements...", "area mean stack standard center bounding integrated redirect=To_Calculate decimal=9");
            run("Analyze Particles...", "  show=Masks display clear in_situ stack");
            saveAs("Results", path+"/Raw_csv_results/"+Dish+"/Particle_information.csv");
            selectWindow("To_Calculate");
            if (White_Bkgrn){               // Red Colonies, and White Background, revert to original color.
                run("Invert", "stack");
            };
            //Spliting image into R,G,B channels.
            selectWindow("To_Calculate");
            run("Split Channels");
            selectWindow("To_Calculate (blue)");
            rename("blue");
            selectWindow("To_Calculate (green)");
            rename("green");
            selectWindow("To_Calculate (red)");
            rename("red");  
            //5) Saving color measurements:
            colors = newArray("red", "green", "blue");
            for (color = 0; color < 3; color++){
                selectWindow("Final_Mask");
                run("Set Measurements...", "mean standard redirect="+colors[color]+" decimal=9");
                run("Analyze Particles...", "  show=Masks display clear  in_situ stack");
                saveAs("Results", path+"/Raw_csv_results/"+Dish+"/Particle_information_"+colors[color]+".csv");
                close(colors[color]);
            }; 
            //5.1) Obtained their color ID based on the Connected Components Labeling 
            selectWindow("Final_Mask");

            run("Set Measurements...", "modal redirect=Labeled_Colonies decimal=1");
            run("Analyze Particles...", "display clear in_situ stack");
            saveAs("Results", path+"/Raw_csv_results/"+Dish+"/Particle_information_IDs.csv");   
            //Restore original values, for next analysis.
            run("Set Measurements...", "area mean stack standard center bounding integrated redirect=None decimal=9");
            run("Set Scale...", "distance=0 global");
            selectWindow("Labeled_Colonies");
            setSlice(1);
            run("Duplicate...", "use");
            saveAs("Tiff", path+"/Raw_csv_results/"+Dish+"/Final_Mask.tif");
            run("Close All");
            if (verbose){
                print("Time elapsed to measure all values from dish "+Dish+":    "+(getTime()-Time)+" ms");  
            };    
        };
        if (isOpen("Log")){
            selectWindow("Log");
            saveAs("Text", path+"/Raw_csv_results/"+Dish+"/Log.txt");  
            close("Log");
        }
        close("Results");
        close("ROI Manager");
    };
    