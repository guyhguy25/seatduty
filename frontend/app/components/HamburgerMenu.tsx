"use client";

import { useState } from "react";
import Link from "next/link";

export default function HamburgerMenu() {
  const [isOpen, setIsOpen] = useState(false);

  const toggleMenu = () => {
    setIsOpen(!isOpen);
  };

  return (
    <div className="relative">
      {/* Hamburger Button */}
      <button
        onClick={toggleMenu}
        className="fixed top-4 left-4 z-50 p-2 bg-gray-800 rounded-lg border border-gray-700 hover:bg-gray-700 transition-colors"
        aria-label="Toggle menu"
      >
        <div className="w-6 h-6 flex flex-col justify-center space-y-1">
          <span className={`block h-0.5 bg-white transition-all duration-300 ${isOpen ? 'rotate-45 translate-y-1.5' : ''}`}></span>
          <span className={`block h-0.5 bg-white transition-all duration-300 ${isOpen ? 'opacity-0' : ''}`}></span>
          <span className={`block h-0.5 bg-white transition-all duration-300 ${isOpen ? '-rotate-45 -translate-y-1.5' : ''}`}></span>
        </div>
      </button>

      {/* Overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-40"
          onClick={toggleMenu}
        ></div>
      )}

      {/* Menu Panel */}
      <div className={`fixed top-0 left-0 h-full w-80 bg-gray-800 border-r border-gray-700 z-50 transform transition-transform duration-300 ${isOpen ? 'translate-x-0' : '-translate-x-full'}`}>
        <div className="p-6">
          {/* Close Button */}
          <button
            onClick={toggleMenu}
            className="absolute top-4 right-4 text-gray-400 hover:text-white transition-colors"
            aria-label="Close menu"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>

          {/* Menu Header */}
          <div className="mb-8">
            <h2 className="text-2xl font-bold text-white mb-2">SeatDuty</h2>
            <p className="text-gray-400">Game Assignment System</p>
          </div>

          {/* Menu Items */}
          <nav className="space-y-4">
            <Link
              href="/"
              onClick={toggleMenu}
              className="flex items-center space-x-3 p-3 rounded-lg hover:bg-gray-700 transition-colors text-white"
            >
              <div className="w-8 h-8 bg-blue-500 rounded-lg flex items-center justify-center">
                <span className="text-white text-sm">⚽</span>
              </div>
              <span className="font-medium">Games</span>
            </Link>

            <Link
              href="/users"
              onClick={toggleMenu}
              className="flex items-center space-x-3 p-3 rounded-lg hover:bg-gray-700 transition-colors text-white"
            >
              <div className="w-8 h-8 bg-green-500 rounded-lg flex items-center justify-center">
                <span className="text-white text-sm">👥</span>
              </div>
              <span className="font-medium">Users</span>
            </Link>

            <Link
              href="/assignments"
              onClick={toggleMenu}
              className="flex items-center space-x-3 p-3 rounded-lg hover:bg-gray-700 transition-colors text-white"
            >
              <div className="w-8 h-8 bg-orange-500 rounded-lg flex items-center justify-center">
                <span className="text-white text-sm">📋</span>
              </div>
              <span className="font-medium">Assignments</span>
            </Link>
          </nav>

          {/* Footer */}
          <div className="absolute bottom-6 left-6 right-6">
            <div className="text-center text-gray-500 text-sm">
              <p>SeatDuty v1.0</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
