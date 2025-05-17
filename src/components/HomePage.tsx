import React, { useEffect } from "react";
import AOS from "aos";
import "aos/dist/aos.css";

interface NavLink {
  name: string;
  href: string;
}

const navLinks: NavLink[] = [
  { name: "Home", href: "#" },
  { name: "Features", href: "#features" },
  { name: "Pricing", href: "#pricing" },
  { name: "Contact", href: "#contact" },
];

const HomePage: React.FC = () => {
  useEffect(() => {
    AOS.init({ duration: 900, once: true });
  }, []);

  return (
    <div className="bg-gradient-to-br from-gray-50 to-gray-200 min-h-screen">
      {/* Sticky Navbar */}
      <nav className="fixed top-0 left-0 w-full z-30 bg-white/60 backdrop-blur-md border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-8 py-3 flex items-center justify-between">
          <span className="text-2xl font-extrabold tracking-tight bg-gradient-to-r from-blue-500 to-purple-600 bg-clip-text text-transparent">
             Brand
          </span>
          <div className="flex gap-8">
            {navLinks.map((link) => (
              <a
                key={link.name}
                href={link.href}
                className="relative text-gray-700 font-medium hover:text-blue-600 transition-colors duration-200
                  after:block after:h-0.5 after:bg-blue-500 after:scale-x-0 hover:after:scale-x-100
                  after:transition-transform after:duration-200 after:origin-left after:mt-1"
              >
                {link.name}
              </a>
            ))}
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="flex flex-col items-center justify-center min-h-screen pt-24 pb-16 text-center">
        <h1
          className="text-5xl md:text-7xl font-extrabold tracking-tight bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-6"
          data-aos="fade-up"
        >
          Experience the Future of Events
        </h1>
        <p
          className="text-lg md:text-2xl text-gray-600 max-w-2xl mx-auto mb-10"
          data-aos="fade-up"
          data-aos-delay="200"
        >
          AI-powered event intelligence and instant highlight reels. Designed for the next generation of experiences.
        </p>
        <a
          href="#features"
          className="inline-block px-8 py-4 rounded-full bg-blue-600 text-white text-lg font-semibold shadow-lg hover:bg-blue-700 transition-all duration-200"
          data-aos="fade-up"
          data-aos-delay="400"
        >
          Get Started
        </a>
      </section>

      {/* Features Section */}
      <section
        id="features"
        className="max-w-5xl mx-auto py-24 px-4 grid md:grid-cols-3 gap-12"
      >
        <div data-aos="fade-up" className="text-center">
          <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-gradient-to-br from-blue-500 to-purple-500 flex items-center justify-center text-white text-3xl">
            🎥
          </div>
          <h3 className="text-xl font-bold mb-2">AI Video Highlights</h3>
          <p className="text-gray-500">Automatically generate stunning highlight reels from your event footage.</p>
        </div>
        <div data-aos="fade-up" data-aos-delay="100" className="text-center">
          <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-gradient-to-br from-blue-500 to-purple-500 flex items-center justify-center text-white text-3xl">
            ⚡
          </div>
          <h3 className="text-xl font-bold mb-2">Real-time Analytics</h3>
          <p className="text-gray-500">Get instant insights and analytics to maximize your event's impact.</p>
        </div>
        <div data-aos="fade-up" data-aos-delay="200" className="text-center">
          <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-gradient-to-br from-blue-500 to-purple-500 flex items-center justify-center text-white text-3xl">
            🛡️
          </div>
          <h3 className="text-xl font-bold mb-2">Privacy First</h3>
          <p className="text-gray-500">Your data is secure and private, always.</p>
        </div>
      </section>

      {/* Pricing Section */}
      <section
        id="pricing"
        className="max-w-4xl mx-auto py-24 px-4"
      >
        <div data-aos="fade-up" className="text-center mb-12">
          <h2 className="text-3xl md:text-4xl font-extrabold mb-4">Simple Pricing</h2>
          <p className="text-gray-500">No hidden fees. Choose the plan that fits your needs.</p>
        </div>
        <div className="flex flex-col md:flex-row gap-8 justify-center">
          <div data-aos="fade-up" className="flex-1 bg-white rounded-2xl shadow-lg p-8 border border-gray-100">
            <h3 className="text-xl font-bold mb-2">Starter</h3>
            <p className="text-3xl font-extrabold mb-4">$19<span className="text-base font-medium">/mo</span></p>
            <ul className="text-gray-500 mb-6 space-y-2 text-left">
              <li>✔️ 10 highlight reels/month</li>
              <li>✔️ Basic analytics</li>
              <li>✔️ Email support</li>
            </ul>
            <button className="w-full py-3 rounded-full bg-blue-600 text-white font-semibold hover:bg-blue-700 transition-all duration-200">Choose Starter</button>
          </div>
          <div data-aos="fade-up" data-aos-delay="100" className="flex-1 bg-white rounded-2xl shadow-lg p-8 border-2 border-blue-600">
            <h3 className="text-xl font-bold mb-2">Pro</h3>
            <p className="text-3xl font-extrabold mb-4">$49<span className="text-base font-medium">/mo</span></p>
            <ul className="text-gray-500 mb-6 space-y-2 text-left">
              <li>✔️ Unlimited highlight reels</li>
              <li>✔️ Advanced analytics</li>
              <li>✔️ Priority support</li>
            </ul>
            <button className="w-full py-3 rounded-full bg-blue-600 text-white font-semibold hover:bg-blue-700 transition-all duration-200">Choose Pro</button>
          </div>
        </div>
      </section>

      {/* Contact Section */}
      <section
        id="contact"
        className="max-w-2xl mx-auto py-24 px-4 text-center"
      >
        <div data-aos="fade-up">
          <h2 className="text-3xl md:text-4xl font-extrabold mb-4">Contact Us</h2>
          <p className="text-gray-500 mb-8">Have questions? Reach out and our team will get back to you.</p>
          <a
            href="mailto:info@yourbrand.com"
            className="inline-block px-8 py-4 rounded-full bg-blue-600 text-white text-lg font-semibold shadow-lg hover:bg-blue-700 transition-all duration-200"
          >
            Email Us
          </a>
        </div>
      </section>

      {/* Footer */}
      <footer className="text-center text-gray-400 py-8 text-sm">
        &copy; {new Date().getFullYear()} YourBrand. All rights reserved.
      </footer>
    </div>
  );
};

export default HomePage; 