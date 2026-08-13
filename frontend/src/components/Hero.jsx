import React from 'react';

const Hero = ({ title, subtitle, backgroundImage }) => {
  return (
    <section
      className="relative h-screen flex items-center justify-center text-white"
      style={{
        backgroundImage: `url(${backgroundImage || '/images/hero-bg.jpg'})`,
        backgroundSize: 'cover',
        backgroundPosition: 'center',
      }}
    >
      <div className="absolute inset-0 bg-black opacity-50" />
      <div className="relative z-10 text-center max-w-3xl px-4">
        <h1 className="text-5xl md:text-6xl font-bold mb-6">
          {title || 'Explore the World'}
        </h1>
        <p className="text-xl md:text-2xl mb-8">
          {subtitle || 'Discover breathtaking destinations with DK Travel'}
        </p>
        <button className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-8 rounded-full transition duration-300">
          Start Your Journey
        </button>
      </div>
    </section>
  );
};

export default Hero;
