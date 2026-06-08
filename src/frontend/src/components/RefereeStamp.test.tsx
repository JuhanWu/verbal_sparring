import { render, screen } from '@testing-library/react'
import RefereeStamp from './RefereeStamp'

test('renders comment text', () => {
  render(<RefereeStamp comment="匕首入心，一字斃命" />)
  expect(screen.getByText('匕首入心，一字斃命')).toBeInTheDocument()
})

test('renders 判 and 決 seal marks', () => {
  render(<RefereeStamp comment="test" />)
  expect(screen.getByText('判')).toBeInTheDocument()
  expect(screen.getByText('決')).toBeInTheDocument()
})
