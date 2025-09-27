// Debug frontend by logging network requests
console.log('Testing API connection...');

// Make a direct fetch request to health endpoint
fetch('http://127.0.0.1:8000/health')
  .then(response => {
    console.log('Response status:', response.status);
    return response.json();
  })
  .then(data => {
    console.log('API response:', data);
  })
  .catch(error => {
    console.error('API request failed:', error);
  });