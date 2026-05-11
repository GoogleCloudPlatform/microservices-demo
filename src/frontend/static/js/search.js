(function () {
  var input = document.getElementById('product-search-input');
  var clearBtn = document.getElementById('search-clear-btn');
  var resultCount = document.getElementById('search-result-count');
  var noResults = document.getElementById('search-no-results');

  if (!input) return;

  var cards = Array.from(document.querySelectorAll('.hot-product-card'));
  var total = cards.length;

  function filter() {
    var term = input.value.trim().toLowerCase();

    if (!term) {
      cards.forEach(function (c) { c.style.display = ''; });
      clearBtn.style.display = 'none';
      resultCount.style.display = 'none';
      noResults.style.display = 'none';
      return;
    }

    var matched = 0;
    cards.forEach(function (c) {
      var nameEl = c.querySelector('.hot-product-card-name');
      var name = nameEl ? nameEl.textContent.toLowerCase() : '';
      if (name.includes(term)) {
        c.style.display = '';
        matched++;
      } else {
        c.style.display = 'none';
      }
    });

    clearBtn.style.display = 'inline-flex';
    resultCount.textContent = 'Showing ' + matched + ' of ' + total + ' products';
    resultCount.style.display = 'block';

    if (matched === 0) {
      noResults.textContent = 'No products found for ‘' + input.value.trim() + '’';
      noResults.style.display = 'block';
    } else {
      noResults.style.display = 'none';
    }
  }

  input.addEventListener('input', filter);

  clearBtn.addEventListener('click', function () {
    input.value = '';
    input.dispatchEvent(new Event('input'));
    input.focus();
  });
}());
