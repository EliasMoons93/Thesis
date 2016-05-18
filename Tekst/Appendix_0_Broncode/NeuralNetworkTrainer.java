import java.io.File;
import java.io.FileNotFoundException;
import java.io.PrintWriter;
import java.util.Arrays;
import java.util.HashSet;
import java.util.Random;
import java.util.Set;


public class Main {
	public static void main(String[] args) throws FileNotFoundException {
		new Main();
	}
	
	private static int NB_HIDDEN_NODES = 6;
	private static final double LEARNING_RATE = 0.35;
	private static double BIAS_1 = 0.0;
	private static double BIAS_2 = 0.0;
	
	private Random random;
	
	private double[][] weights1;
	private double[] weights2;
	
	public Main() throws FileNotFoundException {
		PrintWriter pw = new PrintWriter(new File("weights.txt"));
		random = new Random();
		initializeWeights();
		Set<Sample> trainingData = getTrainingData();
		System.out.println("SIZE TRAININGDATA: " + trainingData.size());
		int count = 0;
		while(count++  < 100000) {
			trainNetwork(trainingData);
			if (count%10000 == 0) System.out.println((count/10000) + " " + (getSquaredError(trainingData)/trainingData.size()));
		}
		printDiffs(trainingData);
		saveWeights(pw);
		pw.close();
	}
	
	
	private void saveWeights(PrintWriter pw) {
		pw.println("WEIGHTS LAYER 1:");
		for (int j = 0; j < NB_HIDDEN_NODES; j++) {
			String line = "";
			for (int i = 0; i < 12; i++) {
				if (i != 0) line += " ";
				line += (String.format("%.2f", weights1[i][j]));
			}
			pw.println(line);
		}
		
		pw.println();
		
		pw.println("WEIGHTS LAYER 2:");
		for (int j = 0; j < NB_HIDDEN_NODES; j++) {
			pw.println(String.format("%.2f",  weights2[j]));
		}
	}
	
	
	private void printDiffs(Set<Sample> testData) {
		for (Sample sample: testData) {
			System.out.println(sample.output + " " + getNetworkValue(sample));
		}
	}
	
	
	private double getNetworkValue(Sample sample) {
		double[] input = sample.getInput();
		
		//calculation of result
		double[] outputsHiddenLayer = new double[NB_HIDDEN_NODES];
		for (int j = 0; j < NB_HIDDEN_NODES; j++) {
			double hiddenSum = BIAS_1;
			for (int i = 0; i < 12; i++) {
				hiddenSum += input[i]*weights1[i][j];
			}
			outputsHiddenLayer[j] = logicalValue(hiddenSum);
		}
		double endSum = BIAS_2;
		for (int j = 0; j < NB_HIDDEN_NODES; j++) {
			endSum += outputsHiddenLayer[j]*weights2[j];
		}
		double result = logicalValue(endSum);
		return result;
	}
	
	
	private double getSquaredError(Set<Sample> testData) {
		double squaredError = 0.0;
		for (Sample sample: testData) {
			double[] input = sample.getInput();
			double output = sample.getOutput();
			double[] outputsHiddenLayer = new double[NB_HIDDEN_NODES];
			for (int j = 0; j < NB_HIDDEN_NODES; j++) {
				double hiddenSum = BIAS_1;
				for (int i = 0; i < 12; i++) {
					hiddenSum += input[i]*weights1[i][j];
				}
				outputsHiddenLayer[j] = logicalValue(hiddenSum);
			}
			double endSum = BIAS_2;
			for (int j = 0; j < NB_HIDDEN_NODES; j++) {
				endSum += outputsHiddenLayer[j]*weights2[j];
			}
			double result = logicalValue(endSum);
			double error = Math.abs(output-result);
			squaredError += error*error;
		}
		return squaredError;
	}
	
	
	private void trainNetwork(Set<Sample> trainingData) {
		for (Sample sample: trainingData) {
			double[] input = sample.getInput();
			double output = sample.getOutput();
			
			//calculation of result
			double[] outputsHiddenLayer = new double[NB_HIDDEN_NODES];
			for (int j = 0; j < NB_HIDDEN_NODES; j++) {
				double hiddenSum = BIAS_1;
				for (int i = 0; i < 12; i++) {
					hiddenSum += input[i]*weights1[i][j];
				}
				outputsHiddenLayer[j] = logicalValue(hiddenSum);
			}
			double endSum = BIAS_2;
			for (int j = 0; j < NB_HIDDEN_NODES; j++) {
				endSum += outputsHiddenLayer[j]*weights2[j];
			}
			double result = logicalValue(endSum);
			double error = output-result;
			
			double[] oldWeights2 = weights2.clone();
			//backpropagation of error
			for (int j = 0; j < NB_HIDDEN_NODES; j++) {
				double diff = LEARNING_RATE * error  * result * (1 - result) * outputsHiddenLayer[j];
				weights2[j] += diff;
			}
			for (int j = 0; j < NB_HIDDEN_NODES; j++) {
				for (int i = 0; i < 12; i++) {
					double diff = LEARNING_RATE * error * outputsHiddenLayer[j] * (1 - outputsHiddenLayer[j]) * input[i] * oldWeights2[j];
					weights1[i][j] += diff;
				}
			}
		}
	}
	
	
	private double logicalValue(double d) {
		return (1 / (1 + Math.exp(-1 * d)));
	}
	
	
	private Set<Sample> getTrainingData() {
		Set<Sample> data = new HashSet<Sample>();
		boolean[] goodDistance = new boolean[]{true, false, false, true, true, true, false, true, true, true, false, false};
		for (int i = 0; i < 12; i++) {
			for (int j = i; j < 12; j++) {
				double[] sampleInput = new double[12];
				Arrays.fill(sampleInput, 0.0);
				sampleInput[i] = 1.0;
				sampleInput[j] = 1.0;
				double sampleOutput;
				if (goodDistance[j-i]) {
					sampleOutput = 0.99;
				} else {
					sampleOutput = 0.01;
				}
				Sample sample = new Sample(sampleInput, sampleOutput);
				data.add(sample);
			}
		}
		return data;
	}
	
	
	private class Sample{
		private double[] input;
		private double output;
		public Sample(double[] input, double output) {
			this.input = input;
			this.output = output;
		}
		
		public double[] getInput() {
			return input;
		}
		
		public double getOutput() {
			return output;
		}
	}
	
	
	private void initializeWeights() {
		weights1 = new double[12][NB_HIDDEN_NODES];
		for (int i = 0; i < 12; i++) {
			for (int j = 0; j < NB_HIDDEN_NODES; j++) {
				weights1[i][j] = random.nextDouble();
			}
		}
		
		weights2 = new double[NB_HIDDEN_NODES];
		for (int i = 0; i < NB_HIDDEN_NODES; i++) {
			weights2[i] = random.nextDouble();
		}
	}
}
