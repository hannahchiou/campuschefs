// code to dynamically add ingredient rows using cloning
// add a blank row when button is clicked

// let count = 0; // track the number of rows added
//document.querySelectorAll('#recipe tbody tr').length
let count = document.querySelectorAll('#recipe tbody tr').length;

document.getElementById('addRowBtn').addEventListener('click', () => {
    // step 1: clone template
    var copy = document.querySelector('#row-template').content.cloneNode(true);
    
    // step 2: modify template
    copy.querySelector("input[name='quantity']").setAttribute('name', `ingredients[${count}][quantity]`);
    copy.querySelector("input[name='measurement']").setAttribute('name', `ingredients[${count}][measurement]`);
    copy.querySelector("input[name='ingredient']").setAttribute('name', `ingredients[${count}][name]`);
    
    // step 3: add to page
    document.querySelector("#recipe tbody").appendChild(copy);
    
    count++;
});