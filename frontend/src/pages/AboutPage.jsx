import React from 'react';

const team = [
  { name: 'Sayan Bhatt', role: 'Lead Developer', emoji: '👨‍💻' },
  { name: 'DK Travel Team', role: 'Design & UX', emoji: '🎨' },
  { name: 'Community', role: 'Feedback & Testing', emoji: '🤝' },
];

const AboutPage = () => {
  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">About DK Travel</h1>
        <p className="text-xl text-gray-600 max-w-2xl mx-auto">
          We believe every journey should be extraordinary. DK Travel helps you
          discover and book the world's most beautiful destinations.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-16">
        <div className="bg-blue-50 rounded-xl p-8">
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">Our Mission</h2>
          <p className="text-gray-700 leading-relaxed">
            To make travel accessible, enjoyable, and stress-free for everyone.
            We curate the best destinations, negotiate the best prices, and
            provide a seamless booking experience.
          </p>
        </div>
        <div className="bg-indigo-50 rounded-xl p-8">
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">Our Vision</h2>
          <p className="text-gray-700 leading-relaxed">
            To become the most trusted travel platform in India, connecting
            millions of travellers with unforgettable experiences across the
            globe.
          </p>
        </div>
      </div>

      <div className="mb-16">
        <h2 className="text-3xl font-bold text-gray-900 text-center mb-8">Our Team</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {team.map((member) => (
            <div key={member.name} className="text-center bg-white rounded-xl shadow-md p-6">
              <div className="text-5xl mb-4">{member.emoji}</div>
              <h3 className="text-lg font-semibold text-gray-900">{member.name}</h3>
              <p className="text-gray-500">{member.role}</p>
            </div>
          ))}
        </div>
      </div>

      <div className="bg-gray-50 rounded-xl p-8 text-center">
        <h2 className="text-2xl font-semibold text-gray-900 mb-4">Why Choose Us?</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-6">
          <div>
            <p className="text-3xl font-bold text-blue-600">500+</p>
            <p className="text-gray-600">Destinations</p>
          </div>
          <div>
            <p className="text-3xl font-bold text-blue-600">50K+</p>
            <p className="text-gray-600">Happy Travellers</p>
          </div>
          <div>
            <p className="text-3xl font-bold text-blue-600">4.8★</p>
            <p className="text-gray-600">Average Rating</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AboutPage;
