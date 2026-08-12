import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import SearchBar from '../components/search/SearchBar';
import { DestinationCard } from '../components/cards';
import { Spinner } from '../components/ui';
import { destinationService } from '../services';

const HomePage = () => {
  const [popular, setPopular] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchPopular = async () => {
      try {
        const data = await destinationService.getPopular(6);
        setPopular(data);
      } catch (err) {
        console.error('Failed to fetch popular destinations:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchPopular();
  }, []);

  const handleSearch = (params) => {
    const searchParams = new URLSearchParams();
    if (params.query) searchParams.set('q', params.query);
    if (params.checkIn) searchParams.set('check_in', params.checkIn);
    if (params.checkOut) searchParams.set('check_out', params.checkOut);
    navigate(`/destinations?${searchParams.toString()}`);
  };

  return (
    <div>
      {/* Hero Section */}
      <section className="relative bg-gradient-to-br from-blue-600 to-indigo-800 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24 md:py-32">
          <div className="text-center mb-10">
            <h1 className="text-4xl md:text-6xl font-bold mb-4">
              Your Journey, Your Way
            </h1>
            <p className="text-xl md:text-2xl text-blue-100 max-w-2xl mx-auto">
              Discover breathtaking destinations and create unforgettable
              memories with DK Travel.
            </p>
          </div>
          <SearchBar onSearch={handleSearch} className="max-w-4xl mx-auto" />
        </div>
      </section>

      {/* Popular Destinations */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="text-center mb-10">
          <h2 className="text-3xl font-bold text-gray-900 mb-2">
            Popular Destinations
          </h2>
          <p className="text-gray-600">
            Explore our most loved travel spots around the world.
          </p>
        </div>

        {loading ? (
          <Spinner className="py-12" />
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {popular.map((dest) => (
              <DestinationCard key={dest._id} destination={dest} />
            ))}
          </div>
        )}
      </section>

      {/* Features Section */}
      <section className="bg-gray-50 py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="text-center p-6">
              <div className="text-4xl mb-4">🌍</div>
              <h3 className="text-xl font-semibold mb-2">Global Destinations</h3>
              <p className="text-gray-600">
                Explore thousands of destinations across every continent.
              </p>
            </div>
            <div className="text-center p-6">
              <div className="text-4xl mb-4">💰</div>
              <h3 className="text-xl font-semibold mb-2">Best Prices</h3>
              <p className="text-gray-600">
                Guaranteed best prices with our price match promise.
              </p>
            </div>
            <div className="text-center p-6">
              <div className="text-4xl mb-4">🛡️</div>
              <h3 className="text-xl font-semibold mb-2">Secure Booking</h3>
              <p className="text-gray-600">
                Book with confidence using our secure payment system.
              </p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default HomePage;
