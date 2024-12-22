import { Toast, ToastContainer } from "react-bootstrap";
import { XCircleFill } from "react-bootstrap-icons";

interface ErrorToastProps {
	showToast: boolean;
	setShowToast: (show: boolean) => void;
	errorTitle: string;
	error: string;
}

const ErrorToast: React.FC<ErrorToastProps> = ({
	showToast,
	setShowToast,
	errorTitle,
	error,
}) => {
	return (
		<ToastContainer position="bottom-center">
			<Toast
				show={showToast}
				onClose={() => setShowToast(false)}
				bg="danger"
				delay={3000}
				autohide
			>
				<Toast.Body className="text-white d-flex align-items-center">
					<XCircleFill className="me-2" />
					<strong className="me-1">{errorTitle}</strong>
					{error}
				</Toast.Body>
			</Toast>
		</ToastContainer>
	);
};

export default ErrorToast;
