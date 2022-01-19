/* This is a script to create a shuffle instance that
1. loads first 10 from json data using fetch 
2. on scroll down, loads more
3. select2 dropwdown with anno labels, filter by label 


TODO 
create the json to fetch 
{ name, thumbnail_url, anno_ids }
what if I could filter the annos by label in the modal? 

*/

var Shuffle = window.Shuffle;
var currentPage = 1;
var totalPages;
var gridContainerElement = document.getElementById('grid');
//var loadMoreButton = document.getElementById('load-more-button');
var shuffleInstance;
// Fetch first page of results from the API.
// You should probably polyfill `fetch` if you're going to copy this demo.
// https://github.com/github/fetch
fetch('../assets/lunr/shuffle.json')
  .then(function (response) {
    return response.json();
  })
  .then(function (response) {
    // Store the total number of pages so we know when to disable the "load more" button.
    totalPages = response.interviews.length;
    let counter = 12;
    // Create and insert the markup.
    var markup = getItemMarkup(response.interviews); //.slice(0, 12));
    appendMarkupToGrid(markup);
    function addMore() {
        if (counter <= totalPages) {
        var markup = getItemMarkup(response.interviews.slice(counter, counter+12));
        appendMarkupToGrid(markup);
        // Save the total number of new items returned from the API.
      var itemsFromResponse = 12;
      // Get an array of elements that were just added to the grid above.
      var allItemsInGrid = Array.from(gridContainerElement.children);
      // Use negative beginning index to extract items from the end of the array.
      var newItems = allItemsInGrid.slice(-itemsFromResponse);

      // Notify the shuffle instance that new items were added.
      shuffleInstance.add(newItems);
        counter += 12;
       
        }
    }

    // Add click listener to button to load the next page.
    //loadMoreButton.addEventListener('click', addMore);

    // Initialize Shuffle now that there are items.
    shuffleInstance = new Shuffle(gridContainerElement, {
      itemSelector: '.js-item',
      sizer: '.my-sizer-element',
    });
    return response;
  });



/**
 * Convert an object to HTML markup for an item.
 * @param {object} dataForSingleItem Data object.
 * @return {string}
 */
function getMarkupFromData(dataForSingleItem) {
  var name = dataForSingleItem.name;
  // https://www.paulirish.com/2009/random-hex-color-code-snippets/
  var randomColor = ('000000' + Math.random().toString(16).slice(2, 8)).slice(-6);
  
  let dataGroups= JSON.stringify(dataForSingleItem.labels);
  
  if (dataGroups === undefined) {
    dataGroups = "";
  }
  return `<figure  class="picture-item rounded js-item img-item col-3@sm col-3@xs" data-groups='${dataGroups}'
  data-date-created="${dataForSingleItem.date}" data-title=""
  data-author="Anne Preston">
    <div >
      <div>
        <div class="aspect aspect--16x9"> 
            <div class="aspect__inner">
        <a href="/interview/${dataForSingleItem.name}.html"  rel="noopener"
            title="${dataForSingleItem.name}"><img 
              src="assets/img/thumbnails/${dataForSingleItem.thumbnail}" alt="${dataForSingleItem.name}" /></a>
      </div>
      </div></div>
    </div>
    <figcaption class="picture-item__title">${dataForSingleItem.name}</figcaption>
  </figure>`;
}



/** 
 * Convert an array of item objects to HTML markup.
 * @param {object[]} items Items array.
 * @return {string}
 */
function getItemMarkup(items) {
  return items.reduce(function (str, item) {
    return str + getMarkupFromData(item);
  }, '');
}

/**
 * Append HTML markup to the main Shuffle element.
 * @param {string} markup A string of HTML.
 */
function appendMarkupToGrid(markup) {
  gridContainerElement.insertAdjacentHTML('beforeend', markup);
}

/**
 * Remove the load more button so that the user cannot click it again.
 */
function replaceLoadMoreButton() {
  var text = document.createTextNode('All users loaded');
  var replacement = document.createElement('p');
  replacement.appendChild(text);
  loadMoreButton.parentNode.replaceChild(replacement, loadMoreButton);
}

function filterShuffle(filter) {
  shuffleInstance.filter(filter);
}