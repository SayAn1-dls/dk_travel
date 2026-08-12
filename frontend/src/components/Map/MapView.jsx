import React, { useState, useCallback, useRef, useEffect } from 'react';
import './MapView.css';

const DEFAULT_CENTER = { lat: 20.5937, lng: 78.9629 }; // India center
const DEFAULT_ZOOM = 5;

const MapView = ({
  destinations = [],
  selectedDestination = null,
  onDestinationSelect,
  center = DEFAULT_CENTER,
  zoom = DEFAULT_ZOOM,
  showUserLocation = false,
}) => {
  const mapRef = useRef(null);
  const [mapInstance, setMapInstance] = useState(null);
  const [userLocation, setUserLocation] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (showUserLocation && navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setUserLocation({
            lat: position.coords.latitude,
            lng: position.coords.longitude,
          });
        },
        (error) => console.warn('Geolocation error:', error.message)
      );
    }
  }, [showUserLocation]);

  const handleMarkerClick = useCallback(
    (destination) => {
      if (onDestinationSelect) {
        onDestinationSelect(destination);
      }
    },
    [onDestinationSelect]
  );

  const calculateDistance = (lat1, lng1, lat2, lng2) => {
    const R = 6371;
    const dLat = ((lat2 - lat1) * Math.PI) / 180;
    const dLng = ((lng2 - lng1) * Math.PI) / 180;
    const a =
      Math.sin(dLat / 2) * Math.sin(dLat / 2) +
      Math.cos((lat1 * Math.PI) / 180) *
        Math.cos((lat2 * Math.PI) / 180) *
        Math.sin(dLng / 2) *
        Math.sin(dLng / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    return Math.round(R * c);
  };

  return (
    <div className="map-container">
      {isLoading && (
        <div className="map-loading">
          <div className="spinner" />
          <p>Loading map...</p>
        </div>
      )}

      <div ref={mapRef} className="map-canvas" />

      {selectedDestination && (
        <div className="map-info-card">
          <h3>{selectedDestination.name}</h3>
          <p>{selectedDestination.description}</p>
          {userLocation && (
            <p className="distance">
              {calculateDistance(
                userLocation.lat,
                userLocation.lng,
                selectedDestination.latitude,
                selectedDestination.longitude
              )}{' '}
              km away
            </p>
          )}
          <div className="map-info-actions">
            <button className="btn-primary">View Details</button>
            <button className="btn-secondary">Add to Itinerary</button>
          </div>
        </div>
      )}

      <div className="map-controls">
        <button className="map-btn" title="Zoom In">+</button>
        <button className="map-btn" title="Zoom Out">-</button>
        {showUserLocation && (
          <button className="map-btn" title="My Location">
            📍
          </button>
        )}
      </div>
    </div>
  );
};

export default MapView;
