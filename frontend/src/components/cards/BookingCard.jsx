import React from 'react';

const statusColors = {
  pending: 'bg-yellow-100 text-yellow-800',
  confirmed: 'bg-green-100 text-green-800',
  cancelled: 'bg-red-100 text-red-800',
  completed: 'bg-blue-100 text-blue-800',
};

const BookingCard = ({ booking, onCancel }) => {
  const { _id, destination_id, check_in, check_out, guests, status, nights } = booking;

  const formatDate = (dateStr) => {
    return new Date(dateStr).toLocaleDateString('en-IN', {
      day: 'numeric',
      month: 'short',
      year: 'numeric',
    });
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 border border-gray-100">
      <div className="flex justify-between items-start mb-4">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">
            Booking #{_id?.slice(-6).toUpperCase()}
          </h3>
          <p className="text-sm text-gray-500">Destination: {destination_id}</p>
        </div>
        <span className={`px-3 py-1 rounded-full text-xs font-medium ${statusColors[status] || 'bg-gray-100 text-gray-800'}`}>
          {status?.charAt(0).toUpperCase() + status?.slice(1)}
        </span>
      </div>

      <div className="grid grid-cols-3 gap-4 mb-4">
        <div>
          <p className="text-xs text-gray-500">Check-in</p>
          <p className="text-sm font-medium">{formatDate(check_in)}</p>
        </div>
        <div>
          <p className="text-xs text-gray-500">Check-out</p>
          <p className="text-sm font-medium">{formatDate(check_out)}</p>
        </div>
        <div>
          <p className="text-xs text-gray-500">Guests</p>
          <p className="text-sm font-medium">{guests} {guests === 1 ? 'guest' : 'guests'}</p>
        </div>
      </div>

      <div className="flex justify-between items-center pt-4 border-t border-gray-100">
        <p className="text-sm text-gray-600">{nights} {nights === 1 ? 'night' : 'nights'}</p>
        {status === 'pending' && onCancel && (
          <button
            onClick={() => onCancel(_id)}
            className="text-red-600 hover:text-red-800 text-sm font-medium"
          >
            Cancel Booking
          </button>
        )}
      </div>
    </div>
  );
};

export default BookingCard;
