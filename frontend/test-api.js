// API Integration Test - Test basic connectivity between frontend and backend
import apiService from '../src/services/api';

async function testApiIntegration() {
  console.log('🔍 Starting API Integration Tests...\n');

  try {
    // Test 1: Health Check
    console.log('1. Testing Health Check...');
    await apiService.healthCheck();
    console.log('✅ Health check passed\n');

    // Test 2: Dashboard Summary
    console.log('2. Testing Dashboard Summary...');
    const dashboard = await apiService.getDashboardSummary();
    console.log('✅ Dashboard Summary:', JSON.stringify(dashboard, null, 2), '\n');

    // Test 3: Recent Products
    console.log('3. Testing Recent Products...');
    const products = await apiService.getRecentProducts(5);
    console.log('✅ Recent Products:', JSON.stringify(products, null, 2), '\n');

    // Test 4: Get Products
    console.log('4. Testing Get Products...');
    const allProducts = await apiService.getProducts({ limit: 10 });
    console.log('✅ Products:', JSON.stringify(allProducts, null, 2), '\n');

    console.log('🎉 All API tests passed successfully!');
    
  } catch (error) {
    console.error('❌ API Test failed:', error);
    
    if (error instanceof Error) {
      console.error('Error message:', error.message);
      console.error('Error stack:', error.stack);
    }
  }
}

// Run the test if this file is executed directly
if (typeof window === 'undefined') {
  testApiIntegration();
}

export { testApiIntegration };