import React from 'react';
import { Link } from 'react-router-dom';

const DestinationCard = ({ destination }) => {
  const {
    _id,
    name,
    country,
    image_url,
    price_per_night,
    rating,
    category,
    description,
  } = destination;

  const renderStars = (rating) => {
    const stars = [];
    const fullStars = Math.floor(rating);
    for (let i = 0; i < 5; i++) {
      stars.push(
        <span key={i} className={i < fullStars ? 'text-yellow-400' : 'text-gray-300'}>★</span>
      );
    }
    return stars;
  };

  return (
    <Link
      to={`/destinations/${_id}`}
      className="group block bg-white rounded-xl shadow-md overflow-hidden hover:shadow-xl transition-shadow duration-300"
    >
      <div className="relative h-48 overflow-hidden">
        <img
          src={image_url || '/placeholder-destination.jpg'}
          alt={name}
          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
          loading="lazy"
        />
        {category && (
          <span className="absolute top-3 left-3 bg-blue-600 text-white text-xs px-2 py-1 rounded-full">
            {category}
          </span>
        )}
      </div>
      <div className="p-4">
        <div className="flex justify-between items-start mb-2">
          <div>
            <h3 className="text-lg font-semibold text-gray-900 group-hover:text-blue-600 transition-colors">{name}</h3>
            <p className="text-sm text-gray-500">{country}</p>
          </div>
          <div className="text-right">
            <p className="text-lg font-bold text-blue-600">₹{price_per_night?.toLocaleString('en-IN')}</p>
            <p className="text-xs text-gray-400">per night</p>
          </div>
        </div>
        <p className="text-sm text-gray-600 mb-3 line-clamp-2">{description}</p>
        <div className="flex items-center">
          <div className="flex">{renderStars(rating || 0)}</div>
          <span className="ml-2 text-sm text-gray-500">{rating?.toFixed(1)}</span>
        </div>
      </div>
    </Link>
  );
};

export default DestinationCard;
