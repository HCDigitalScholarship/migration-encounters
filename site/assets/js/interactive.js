// function for enlarging the central gallery image
function openScaled(imgs) {
    var expandImg = document.getElementById("expandedImg");
    var imgText = document.getElementById("imgtext");

    expandImg.src = imgs.src;
    imgText.innerHTML = imgs.alt;
    expandImg.parentElement.style.display = "block";
    console.log("clicked on image")
}







function search_transcript(){
    let input = document.getElementById('search_text').value
    input=input.toLowerCase();
    let pArray = document.getElementsByName('p');
    let resultsParagraph = document.getElementById("search_results");
    resultsParagraph.innerHTML = ""
  
    for (i = 0; i < pArray.length; i++) { 
      console.log("going through a paragraph ", i);
      if (pArray[i].innerText.toLowerCase().includes(input)){
        pArray[i].style.backgroundColor = "#ccc";    
        console.log("found in paragraph ", i);
        let tempParagraph = document.createElement("p");
        tempParagraph.className = "response_paragraph";
        resultsParagraph.appendChild(tempParagraph);
        let tempLink = document.createElement("a");
        tempLink.className = "response_link";
        tempParagraph.appendChild(tempLink);
        tempLink.innerText = "found in paragraph "+(i+1);   
        pArray[i].id = "paragraph" + i; 
        tempLink.href = "#" + pArray[i].id;
      }
      resultsParagraph.style.display = "inline-block";
    } 
  }
// {"mode":"full","isActive":false}