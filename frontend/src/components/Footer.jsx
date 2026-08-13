import React from 'react';

const Footer = () => {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="bg-gray-900 text-white py-8">
      <div className="container mx-auto px-4">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div>
            <h3 className="text-xl font-bold mb-4">DK Travel</h3>
            <p className="text-gray-400">Your trusted travel companion for unforgettable journeys.</p>
          </div>
          <div>
            <h4 className="font-semibold mb-3">Quick Links</h4>
            <ul className="space-y-2 text-gray-400">
              <li><a href="/destinations">Destinations</a></li>
              <li><a href="/packages">Packages</a></li>
              <li><a href="/contact">Contact Us</a></li>
            </ul>
          </div>
          <div>
            <h4 className="font-semibold mb-3">Contact</h4>
            <p className="text-gray-400">info@dktravel.com</p>
            <p className="text-gray-400">+91 98765 43210</p>
          </div>
        </div>
        <div className="border-t border-gray-700 mt-8 pt-4 text-center text-gray-500">
          <p>&copy; {currentYear} DK Travel. All rights reserved.</p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
