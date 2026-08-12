import React from 'react';
import { Link } from 'react-router-dom';
import { Button } from '../components/ui';

const NotFoundPage = () => {
  return (
    <div className="min-h-[70vh] flex items-center justify-center px-4">
      <div className="text-center">
        <h1 className="text-9xl font-bold text-blue-600 mb-4">404</h1>
        <h2 className="text-3xl font-semibold text-gray-900 mb-4">
          Page Not Found
        </h2>
        <p className="text-gray-600 mb-8 max-w-md mx-auto">
          Oops! Looks like this destination doesn't exist. Let's get you
          back on track.
        </p>
        <div className="flex gap-4 justify-center">
          <Link to="/">
            <Button>Go Home</Button>
          </Link>
          <Link to="/destinations">
            <Button variant="outline">Explore Destinations</Button>
          </Link>
        </div>
      </div>
    </div>
  );
};

export default NotFoundPage;
