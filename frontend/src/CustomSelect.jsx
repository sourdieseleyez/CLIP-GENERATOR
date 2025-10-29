import { useState, useRef, useEffect } from 'react';
import { ChevronDown } from 'lucide-react';
import './CustomSelect.css';

function CustomSelect({ value, onChange, options, disabled = false }) {
  const [isOpen, setIsOpen] = useState(false);
  const selectRef = useRef(null);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (selectRef.current && !selectRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSelect = (optionValue) => {
    onChange({ target: { value: optionValue } });
    setIsOpen(false);
  };

  const selectedOption = options.find(opt => opt.value === value);

  return (
    <div className={`custom-select ${isOpen ? 'open' : ''} ${disabled ? 'disabled' : ''}`} ref={selectRef}>
      <div 
        className="custom-select-trigger" 
        onClick={() => !disabled && setIsOpen(!isOpen)}
      >
        <span>{selectedOption?.label || 'Select...'}</span>
        <ChevronDown size={14} className={`chevron ${isOpen ? 'rotated' : ''}`} />
      </div>
      
      {isOpen && (
        <div className="custom-select-dropdown">
          {options.map((option) => (
            <div
              key={option.value}
              className={`custom-select-option ${option.value === value ? 'selected' : ''}`}
              onClick={() => handleSelect(option.value)}
            >
              {option.label}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default CustomSelect;
