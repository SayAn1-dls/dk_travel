import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Spinner, Button } from '../components/ui';
import { destinationService, bookingService } from '../services';

const DestinationDetailPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [destination, setDestination] = useState(null);
  const [loading, setLoading] = useState(true);
  const [bookingForm, setBookingForm] = useState({
    check_in: '',
    check_out: '',
    guests: 1,
    special_requests: '',
  });
  const [booking, setBooking] = useState(false);

  useEffect(() => {
    const fetchDestination = async () => {
      try {
        const data = await destinationService.getById(id);
        setDestination(data);
      } catch (err) {
        console.error('Failed to fetch destination:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchDestination();
  }, [id]);

  const handleBooking = async (e) => {
    e.preventDefault();
    setBooking(true);
    try {
      await bookingService.create({
        destination_id: id,
        ...bookingForm,
      });
      navigate('/bookings');
    } catch (err) {
      console.error('Booking failed:', err);
      alert('Booking failed. Please try again.');
    } finally {
      setBooking(false);
    }
  };

  if (loading) return <Spinner className="py-24" size="lg" />;
  if (!destination) {
    return (
      <div className="text-center py-24">
        <h2 className="text-2xl font-semibold text-gray-700">Destination not found</h2>
        <Button variant="outline" className="mt-4" onClick={() => navigate('/destinations')}>
          Browse Destinations
        </Button>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Details */}
        <div className="lg:col-span-2">
          <img
            src={destination.image_url || '/placeholder-destination.jpg'}
            alt={destination.name}
            className="w-full h-80 object-cover rounded-xl mb-6"
          />
          <h1 className="text-3xl font-bold text-gray-900 mb-2">{destination.name}</h1>
          <p className="text-gray-500 mb-4">{destination.country}</p>
          <div className="flex items-center gap-4 mb-6">
            <span className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm">
              {destination.category}
            </span>
            <span className="text-yellow-500">★ {destination.rating?.toFixed(1)}</span>
            <span className="text-2xl font-bold text-blue-600">
              ₹{destination.price_per_night?.toLocaleString('en-IN')}
              <span className="text-sm text-gray-400 font-normal"> / night</span>
            </span>
          </div>
          <div className="prose max-w-none">
            <p className="text-gray-700 leading-relaxed">{destination.description}</p>
          </div>
        </div>

        {/* Booking Form */}
        <div className="bg-white rounded-xl shadow-lg p-6 h-fit sticky top-24">
          <h2 className="text-xl font-semibold mb-4">Book This Destination</h2>
          <form onSubmit={handleBooking} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Check-in</label>
              <input
                type="date"
                required
                value={bookingForm.check_in}
                onChange={(e) => setBookingForm({ ...bookingForm, check_in: e.target.value })}
                min={new Date().toISOString().split('T')[0]}
                className="w-full border rounded-lg px-3 py-2"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Check-out</label>
              <input
                type="date"
                required
                value={bookingForm.check_out}
                onChange={(e) => setBookingForm({ ...bookingForm, check_out: e.target.value })}
                min={bookingForm.check_in || new Date().toISOString().split('T')[0]}
                className="w-full border rounded-lg px-3 py-2"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Guests</label>
              <select
                value={bookingForm.guests}
                onChange={(e) => setBookingForm({ ...bookingForm, guests: parseInt(e.target.value) })}
                className="w-full border rounded-lg px-3 py-2"
              >
                {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((n) => (
                  <option key={n} value={n}>{n} {n === 1 ? 'Guest' : 'Guests'}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Special Requests</label>
              <textarea
                value={bookingForm.special_requests}
                onChange={(e) => setBookingForm({ ...bookingForm, special_requests: e.target.value })}
                rows={3}
                className="w-full border rounded-lg px-3 py-2"
                placeholder="Any special requirements..."
              />
            </div>
            <Button type="submit" loading={booking} className="w-full">
              Book Now
            </Button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default DestinationDetailPage;
