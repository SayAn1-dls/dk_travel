import React, { useState } from 'react';

const Contact = () => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    subject: '',
    message: '',
  });

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    console.log('Contact form submitted:', formData);
    alert('Thank you! We will get back to you shortly.');
    setFormData({ name: '', email: '', subject: '', message: '' });
  };

  return (
    <div className="max-w-2xl mx-auto py-12 px-4">
      <h1 className="text-3xl font-bold mb-8">Contact Us</h1>
      <form onSubmit={handleSubmit} className="space-y-6">
        <input type="text" name="name" value={formData.name} onChange={handleChange} placeholder="Your Name" required className="w-full p-3 border rounded" />
        <input type="email" name="email" value={formData.email} onChange={handleChange} placeholder="Email Address" required className="w-full p-3 border rounded" />
        <input type="text" name="subject" value={formData.subject} onChange={handleChange} placeholder="Subject" required className="w-full p-3 border rounded" />
        <textarea name="message" value={formData.message} onChange={handleChange} placeholder="Your Message" rows="5" required className="w-full p-3 border rounded" />
        <button type="submit" className="bg-blue-600 text-white py-3 px-6 rounded hover:bg-blue-700">Send Message</button>
      </form>
    </div>
  );
};

export default Contact;
